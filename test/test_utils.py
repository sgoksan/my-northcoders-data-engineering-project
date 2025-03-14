from src.src_ingestion.utils import (
    get_s3_client,
    get_secrets_manager_client,
    upload_to_s3,
    fetch_latest_update_time_from_s3,
    fetch_latest_update_time_from_db,
    fetch_snapshot_of_table_from_db,
    retrieval,
    connect_to_db,
    close_db_connection,
)
import boto3
import unittest
from unittest.mock import patch, Mock
from moto import mock_aws
import json
from botocore.exceptions import ClientError
import io
import logging
import datetime
from pg8000.native import Connection


def input_args():
    yield "bidenj"
    yield "Pa55word"
    yield "host"
    yield "database"
    yield "port"
    yield "bidenj"
    yield "Pa55word"
    yield "host"
    yield "database"
    yield "port"


def input_args_2():
    yield "bidenj"
    yield "Pa55word"
    yield "host"
    yield "database"
    yield "port"
    # yield "abc"


def entry(client, secret_identifier="de_2024_12_02"):
    """Use to create the initial TEST secret"""
    if "SecretsManager" in str(type(client)):
        get_username = "test"
        get_password = "test"
        get_host = "test"
        get_database = "test"
        get_port = "test"
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


class TestEntry:
    @patch("builtins.input", side_effect=input_args())
    def test_entry_successful(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                entry(client)
                secret = client.get_secret_value(SecretId="de_2024_12_02")
                assert secret is not None

    @patch("builtins.input", side_effect=input_args())
    def test_entry_fails(self, mock_input):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                entry(client)
                result = fake_out.getvalue()
                assert (
                    "invalid client type used for secret manager! plz contact developer!"
                    in result
                )

    @patch("builtins.input", side_effect=input_args())
    def test_entry_successfully_stored(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            entry(client)
            response = client.list_secrets()
            assert len(response["SecretList"]) == 1

    @patch("builtins.input", side_effect=input_args())
    def test_secret_already_exists(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            entry(client)
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                entry(client)
                result = fake_out.getvalue()
                assert "Secret already exists!" in result


class TestRetrieval:
    @patch("builtins.input", side_effect=input_args())
    def test_retrieval_successful_1_secret(self, mock_input):
        mock_input.input_args = ["de_2024_12_02"]
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            entry(client)
            res = retrieval(client)
            assert res is not None

    @patch("builtins.input", side_effect=input_args())
    def test_retrieval_successful_return_dict(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                entry(client)
                res = retrieval(client)
                mock_input.input_args = ["de_2024_12_02"]
                assert res == {
                    "username": "test",
                    "password": "test",
                    "host": "test",
                    "database": "test",
                    "port": "test",
                }

    @patch("builtins.input")
    def test_retrieval_secret_doesnot_exist(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                retrieval(client)
                result = fake_out.getvalue()
                assert (
                    "An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation"
                    in result
                )

    def test_retrieval_secret_resource_not_found_error_log(self, caplog):
        with mock_aws():
            with caplog.at_level(logging.WARNING):
                client = boto3.client("secretsmanager", region_name="eu-west-2")
                retrieval(client, "secret")
                assert "Secret does not exist" in caplog.text

    def test_retrieval_secret_general_critical_log(self, caplog):
        with mock_aws():
            with caplog.at_level(logging.CRITICAL):
                client = boto3.client("secretsmanager", region_name="eu-west-2")
                retrieval(client, 11)
                assert (
                    "There has been a critical error when attempting to retrieve secret for totesys DB credentials"
                    in caplog.text
                )


class TestFetchSnapshotOfWholeTable:
    def test_returns_dictionary_result_with_columns_and_data_keys(self):
        mock_conn = Mock()
        mock_conn.run.return_value = [1, "Jeremie", "Franey", 2, "email"]
        mock_conn.columns = [
            {"name": "id"},
            {"name": "first_name"},
            {"name": "last_name"},
            {"name": "department_id"},
            {"name": "email"},
        ]
        result = fetch_snapshot_of_table_from_db(mock_conn, "mock_table")
        assert type(result) == dict
        assert result["columns"]
        assert result["data"]

    def test_fetch_snapshot_handles_critical_error(self, caplog):
        mock_conn = Mock()
        mock_conn.run.side_effect = TypeError
        with caplog.at_level(logging.CRITICAL):
            fetch_snapshot_of_table_from_db(mock_conn, "mock_table")
            assert "Unable to get snapshot of table"


class TestConnectToDB:
    @patch("builtins.input", side_effect=input_args_2())
    def test_connect_to_db_DatabaseError(self, mock_input, caplog):
        with mock_aws():
            with caplog.at_level(logging.CRITICAL):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    connect_to_db("test")
                    assert "The connection to the totesys DB is failing" in caplog.text


class TestCloseDBConnection:
    def test_close_db_connection_exception(self, caplog):
        with mock_aws():
            with caplog.at_level(logging.WARNING):
                connection = "test"
                close_db_connection(connection)
                assert (
                    "The connection to the totesys DB is not able to close"
                    in caplog.text
                )


class TestGetS3Client(unittest.TestCase):
    def test_get_s3_client_success(self):
        client = get_s3_client()
        assert "S3" in str(type(boto3.client("s3")))

    @patch("boto3.client")
    def test_get_s3_client_fail(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Simulated error"}},
            "ListObjects",
        )
        with self.assertRaises(ClientError) as context:
            get_s3_client()
        assert "failed to connect to s3" in str(context.exception)


class TestGetSMClient(unittest.TestCase):
    def test_get_s3_client_success(self):
        client = get_secrets_manager_client()
        assert "SecretsManager" in str(
            type(boto3.client("secretsmanager", region_name="eu-west-2"))
        )

    @patch("boto3.client")
    def test_get_s3_client_fail(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Simulated error"}},
            "ListObjects",
        )
        with self.assertRaises(ClientError) as context:
            get_secrets_manager_client()
        assert "failed to connect to secret manager" in str(context.exception)


class TestUploadS3:
    def test_upload_to_s3(self):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            client.create_bucket(
                Bucket="test-bucket",
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            bucket_name = "test-bucket"
            table = "table"
            result = {"key": "value"}
            object_name = upload_to_s3(bucket_name, table, result, client)
            # Verify the object was uploaded
            response = client.list_objects_v2(Bucket=bucket_name)
            assert "Contents" in response
            keys = [obj["Key"] for obj in response["Contents"]]
            assert object_name in keys
            # Verify the content
            s3_object = client.get_object(Bucket=bucket_name, Key=object_name)
            content = json.loads(s3_object["Body"].read().decode("utf-8"))
            assert content == result

    def test_upload_to_s3_client_error(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "test-bucket"
            table = "table"
            result = {"key": "value"}
            with caplog.at_level(logging.CRITICAL):
                upload_to_s3(bucket_name, table, result, client)
                assert "Unable to put" in caplog.text
                assert "object in ingestion s3 bucket" in caplog.text


class TestFetchLatestUpdateS3:
    def test_fetch_latest_update_time_from_s3(self):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "test-bucket"
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            objects = [
                "table/20250301174108.json",
                "table/20250302140516.json",
                "table/20250103131459.json",
            ]
            for i in objects:
                client.put_object(Bucket=bucket_name, Key=i, Body="test")
            assert (
                fetch_latest_update_time_from_s3(client, bucket_name, "table")
                == 20250302140516
            )

    def test_fetch_latest_time_from_s3_client_error(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "test-bucket"
            table = "table"
            result = {"key": "value"}
            with caplog.at_level(logging.ERROR):
                fetch_latest_update_time_from_s3(client, bucket_name, table)
                assert "Unable to connect to s3 ingestion bucket" in caplog.text

    def test_fetch_latest_time_from_s3_critical_error(self, caplog):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            bucket_name = "test-bucket"
            table = "table"
            result = {"key": "value"}
            with caplog.at_level(logging.CRITICAL):
                fetch_latest_update_time_from_s3(client, bucket_name, table)
                assert "Unable to return the time of the latest" in caplog.text


class TestFectchLatestUpdateDB:
    def test_fetch_latest_upload_when_s3_is_empty(self):
        mock_conn = Mock()
        mock_conn.run.return_value = [
            [datetime.datetime(2022, 11, 3, 14, 20, 49, 962000)]
        ]
        result = fetch_latest_update_time_from_db(mock_conn, "mock_table")
        assert result == 20221103142049

    def test_fetch_latest_time_from_db_critical(self, caplog):
        with mock_aws():
            conn = "test"
            table = 5
            with caplog.at_level(logging.CRITICAL):
                fetch_latest_update_time_from_db(conn, table)
                assert "Unable to return the time of the latest" in caplog.text
