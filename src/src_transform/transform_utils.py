import pandas as pd
import boto3
import json
from io import BytesIO
from botocore.exceptions import ClientError
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_s3_client():
    """Creates s3 client

    Returns:
    - boto3.client: S3 client object

    Exceptions:
    - ClientError: Cannot create s3 client

    Exceptions raised:
    - RuntimeError: "failed to connect to s3, error message as 'error'."
    """
    try:
        client = boto3.client("s3")
        return client
    except ClientError as e:
        logger.error("Unable to create s3 client, %s", str(e))
        raise RuntimeError("failed to connect to s3, error message as {e}") from e


def get_s3_object(client, bucket, key):
    """Gets the file from s3 bucket

    Positional arguments:
    - client (boto3.client): s3 client
    - bucket (str): Name for the ingestion bucket
    - key (str): table file name

    Returns:
    - s3 object dictionary response

    Exceptions:
    - ClientError: Cannot connect to s3 client
    """
    try:
        s3_obj = client.get_object(Bucket=bucket, Key=key)
        s3_obj_bytes = s3_obj["Body"].read()
        s3_obj_dict = json.loads(s3_obj_bytes.decode("utf-8"))
        return s3_obj_dict
    except ClientError as e:
        logger.critical("Unable to get object from Ingestion Bucket, %s", str(e))
        print("Client Error as: %s", str(e))


def convert_s3_obj_to_df(s3_obj_dict):
    """Converts s3 object contents to panda dataframe

    Positional arguments:
    - s3_obj_dict (dict): s3 object dictionary response

    Returns:
    - Table formatted as panda dataframe

    Exceptions:
    - KeyError: Key does not exist in dictionary
    - TypeError: Type of input object is not a dictionary
    - Exception: General error
    """
    try:
        data = s3_obj_dict["data"]
        columns = s3_obj_dict["columns"]
        df = pd.DataFrame(data, columns=columns)
        return df
    except KeyError as e:
        logger.error(
            "Key Error when converting s3 object to panda data frame, %s", str(e)
        )
        print("Key Error as: ", e)
    except TypeError as e:
        logger.error(
            "Type Error when converting s3 object to panda data frame, %s", str(e)
        )
        print("Type Error: %s", str(e))
    except Exception as e:
        logger.critical(
            "Error when converting s3 object to panda data frame, %s", str(e)
        )


def convert_df_to_s3_obj(client, df, bucket, key):
    """Converts panda dataframe to s3 parquet object

    Positional arguments:
    - client (boto3.client): s3 client
    - df (panda df obj): The table in dataframe format
    - bucket (str): Name for the processed bucket
    - key (str): table file name

    Exceptions:
    - ClientError: Cannot connect to s3 client
    - Exception: General error
    """
    try:
        output_buffer = BytesIO()
        df.to_parquet(output_buffer)
        body = output_buffer.getvalue()
        client.put_object(Bucket=bucket, Key=key, Body=body)
        return True
    except ClientError as e:
        logger.error(
            "S3 Client Error when converting panda dataframe to s3 object, %s", str(e)
        )
        print("Client Error as: %s", str(e))
        return False
    except Exception as e:
        logger.critical(
            "Error when converting panda data frame to s3 object, %s", str(e)
        )
        return False
