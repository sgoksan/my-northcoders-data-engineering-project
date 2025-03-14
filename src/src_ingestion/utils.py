import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime
from pg8000.native import Connection, DatabaseError, InterfaceError, identifier
import sys
import logging

sys.path.append("src/src_ingestion")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def entry(client):
    """This function has been depricated"""
    if "SecretsManager" in str(type(client)):
        secret_identifier = "de_2024_12_02"
        get_username = input("Please enter your username: ")
        get_password = input("Please enter your password:")
        get_host = input("Please enter your host: ")
        get_database = input("Please enter your database: ")
        get_port = input("Please enter your port: ")
        secret_value = {
            "username": get_username,
            "password": get_password,
            "host": get_host,
            "database": get_database,
            "port": get_port,
        }
        secret_string = json.dumps(secret_value)
        try:
            client.create_secret(Name=secret_identifier, SecretString=secret_string)
            print("Secret saved.")
        except client.exceptions.ResourceExistsException as e:
            print("Secret already exists!")
        except Exception as err:
            print({"ERROR": err, "message": "Fail to connect to aws secret manager!"})
    else:
        print("invalid client type used for secret manager! plz contact developer!")


def retrieval(client, secret_identifier="de_2024_12_02"):
    """Retrieve a secret called de_2024_12_02 from aws secrets manager

    Arguments:
    - client (boto3.client): AWS secrets manager client
    - secret_identifier (str): Name of secret storing totesys credentials
                                Default = de_2024_12_02

    Returns:
    - res_dict (dict): Returns secret for the Totesys DB connection in dict format

    Exceptions:
    - ResourceNotFoundException: Secret ID does not exist
    - Exception: General error
    """
    if "SecretsManager" in str(type(client)):
        try:
            response = client.get_secret_value(SecretId=secret_identifier)
            res_str = response["SecretString"]
            res_dict = json.loads(res_str)
            return res_dict
        except client.exceptions.ResourceNotFoundException as err:
            print(err)
            logger.warning("Secret does not exist, %s", str(err))
        except Exception as err:
            print(
                {"CRITICAL": err, "message": "Fail to connect to aws secret manager!"}
            )
            logger.critical(
                "There has been a critical error when attempting to retrieve secret for totesys DB credentials, %s",
                str(err),
            )
    else:
        print("invalid client type used for secret manager! plz contact developer!")


def connect_to_db(secret_identifier="de_2024_12_02"):
    """Establish connection to totesys database returns connection

    Keyword argument:
    - secret_identifier (str): Name of secret storing totesys credentials
                                Default = de_2024_12_02

    Returns:
    - pg8000.native.Connection: Connection to totesys database

    Exceptions:
    - InteraceError: Failed to connect to s3 client
    """
    client = get_secrets_manager_client()
    credentials = retrieval(client, secret_identifier=secret_identifier)
    try:
        if not credentials:
            entry(client)
            credentials = retrieval(client)

        return Connection(
            user=credentials["username"],
            password=credentials["password"],
            database=credentials["database"],
            host=credentials["host"],
        )
    except InterfaceError as err:
        logger.critical("The connection to the totesys DB is failing, %s", str(err))


def close_db_connection(conn):
    """Close connection to totesys database

    Positional argument:
    - conn (pg8000.native.Connection): Connection to totesys database

    Exceptions:
    - Exception: General error
    """
    try:
        conn.close()
    except Exception as err:
        logger.warning(
            "The connection to the totesys DB is not able to close, %s", str(err)
        )


def get_s3_client():
    """Creates s3 client returns client

    Return:
    - boto3.client: S3 client object

    Exceptions raised:
    - ClientError: Failed to connect to s3 client
    """
    try:
        client = boto3.client("s3", region_name="eu-west-2")
        return client
    except ClientError as err:
        logger.error("Unable to create s3 client, %s", str(err))
        raise ClientError(
            {
                "Error": {
                    "Code": "FailedToConnect",
                    "Message": "failed to connect to s3",
                }
            },
            "GetS3Client",
        )


def get_secrets_manager_client():
    """Creates secretsmanager client

    Returns:
    - boto3.client: Secretsmanager client object

    Exceptions raised:
    - ClientError: Failed to connect to secretsmanager client
    """
    try:
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        return client
    except ClientError as err:
        logger.error("Unable to create secrets manager client, %s", str(err))
        raise ClientError(
            {
                "Error": {
                    "Code": "FailedToConnect",
                    "Message": "failed to connect to secret manager",
                }
            },
            "GetSecretsManagerClient",
        )


def upload_to_s3(bucket_name, table, result, s3_client):
    """Uploads given file to s3 bucket

    Positional arguments:
    - bucket_name (str): Name for the ingestion bucket
    - table (str): Table from totesys database
    - result (str): Table file name
    - s3_client (boto3.client): S3 client

    Returns:
    - Date formatted json filename (str)

    Exceptions:
    - ClientError: Failed to connect to s3 client
    """
    tmp_file_path = f"/tmp/{table}.json"
    try:
        with open(tmp_file_path, "w") as f:
            filedatain = json.dumps(result, indent=4, sort_keys=True, default=str)
            res_bytes = filedatain.encode("utf-8")

        y_m_d = datetime.now().strftime("%Y%m%d")
        filename = datetime.now().strftime("%H%M%S")
        object_name = f"{table}/{y_m_d}{filename}.json"
        s3_client.put_object(Body=res_bytes, Bucket=bucket_name, Key=object_name)
        return object_name
    except ClientError as err:
        logger.critical(
            "Unable to put %s object in ingestion s3 bucket , %s", str(table), str(err)
        )


def fetch_latest_update_time_from_s3(client, bucket_name, table_name):
    """Fetch latest file loaded to s3 bucket

    Positional arguments:
    - client (boto3.client): S3 client
    - bucket_name (str): Ingestion s3 bucket name
    - table_name (str): Table from totesys database name

    Returns:
    - Latest uploaded file time (int)

    Exceptions:
    - ClientError: Failed to connect to s3 client
    - Exception: General error
    """
    try:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=table_name + "/")
        raw_all_updates = response.get("Contents", [])
        if raw_all_updates:
            all_tables = [update["Key"].split("/")[0] for update in raw_all_updates]
            if table_name not in all_tables:
                return 20000101000001
            all_updates = [
                update["Key"].split("/")[-1][:-5] for update in raw_all_updates
            ]
            last_update = max(list(map(int, all_updates)))
            return last_update
        return 20000101000001
    except ClientError as err:
        logger.error(
            "Unable to connect to s3 ingestion bucket to get latest loaded file, %s",
            str(err),
        )
    except Exception as err2:
        logger.critical(
            "Unable to return the time of the latest loaded file %s to s3, %s",
            str(table_name),
            str(err2),
        )


def fetch_latest_update_time_from_db(conn, table_name):
    """Fetch the latest update of the table in db

    Positional arguments:
    - conn (pg8000.native.Connection): Connection to totesys database
    - table_name (str): Table from totesys database name

    Returns:
    - Latest updated table in database (int)

    Exceptions:
    - Exception: General error
    """
    try:
        query = (
            f"SELECT last_updated FROM {table_name} ORDER BY last_updated DESC LIMIT 1;"
        )
        raw_last_updated = conn.run(query)
        print(raw_last_updated)
        last_updated_dt = raw_last_updated[0][0]
        formatted_res = int(last_updated_dt.strftime("%Y%m%d%H%M%S"))
        return formatted_res
    except Exception as err:
        logger.critical(
            "Unable to return the time of the latest update of table %s, %s",
            str(table_name),
            str(err),
        )


def fetch_snapshot_of_table_from_db(conn, table_name):
    """Fetch a snapshot of one table from ToteSys in it's current state

    Positional arguments:
     - conn (pg8000.native.Connection): Connection to totesys database
     - table_name (str): Table from totesys database name

    Returns:
     - Dictionary containing column names and raw data from the named table.

    Exceptions:
     - Exception: General error
    """
    try:
        raw_data = conn.run(f"SELECT * FROM {identifier(table_name)};")
        columns = [col["name"] for col in conn.columns]
        result = {"columns": columns, "data": raw_data}
        return result
    except Exception as err:
        logger.critical(
            "Unable to get snapshot of table %s, %s", str(table_name), str(err)
        )
