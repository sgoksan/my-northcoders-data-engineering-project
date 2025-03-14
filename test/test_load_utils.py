import boto3, io, logging, unittest, json
from unittest.mock import patch, Mock
from moto import mock_aws
import pandas as pd
from io import BytesIO
from botocore.exceptions import ClientError
from pg8000 import DatabaseError, InterfaceError

from src.src_load.load_utils import (
    pd_read_s3_parquet,
    connect_to_dw,
    get_insert_query,
    retrieval,
    load_tables_to_dw,
    get_column_names,
    get_s3_client,
)


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


class TestLoadLambdaRetrieval:
    @patch("builtins.input", side_effect=input_args())
    def test_retrieval_successfully_gets_a_secret(self, mock_input):
        mock_input.input_args = ["fake_db"]
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            entry(client, secret_identifier="totesys_data_warehouse_olap")
            res = retrieval(client)
            assert res is not None

    @patch("builtins.input")
    def test_retrieval_successful_return_dict(self, mock_input):
        with mock_aws():
            client = boto3.client("secretsmanager", region_name="eu-west-2")
            with patch("sys.stdout", new=io.StringIO()):
                entry(client, secret_identifier="totesys_data_warehouse_olap")
                res = retrieval(client)
                mock_input.input_args = ["fake_tote_dw"]
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

    def test_retrieval_secret_generates_critical_logging_error(self, caplog):
        with mock_aws():
            with caplog.at_level(logging.CRITICAL):
                client = boto3.client("secretsmanager", region_name="eu-west-2")
                retrieval(client, 11)
                assert "critical error " in caplog.text


class TestGetS3Client(unittest.TestCase):
    @patch("boto3.client")
    def test_loggings_for_get_s3_client(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Simulated error"}},
            "ListObjects",
        )
        with self.assertRaises(ClientError) as context:
            get_s3_client()
        assert "failed to connect to s3" in str(context.exception)


class TestPdReadParquett:
    def test_pd_read_s3_parquet(self):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="eu-west-2")
            s3_client.create_bucket(
                Bucket="test-bucket",
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            bucket_name = "test-bucket"
            test_data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(test_data)
            output_buffer = BytesIO()
            df.to_parquet(output_buffer)
            body = output_buffer.getvalue()
            s3_client.put_object(Bucket=bucket_name, Key="test_data_parquet", Body=body)
            res_df = pd_read_s3_parquet("test_data_parquet", bucket_name, s3_client)
            pd.testing.assert_frame_equal(res_df, df)

    def test_pd_read_s3_parquet_returns_critical_log(
        self,
        s3_client,
        create_bucket_processed,
        bucket_name_processed,
        object_key,
        caplog,
    ):
        with mock_aws():
            with caplog.at_level(logging.CRITICAL):
                pd_read_s3_parquet(object_key, 11, s3_client)
                assert "critical error" in caplog.text


class TestConnectToDW:
    @patch("builtins.input", side_effect=input_args())
    def test_connect_to_db_DatabaseError(self, mock_input, caplog):
        with mock_aws():
            with caplog.at_level(logging.CRITICAL):
                connect_to_dw("test")
                assert "The connection to the Data Warehouse is failing" in caplog.text


class TestGetInsertQuery:
    def test_get_insert_query_not_on_conflict(self):
        table_name = "dim_currency"
        column_names = ["currency_id", "currency_code", "currency_name"]
        on_conflict = True
        res = get_insert_query(table_name, column_names, "currency_id", on_conflict)
        print(res)
        expected = """INSERT INTO dim_currency (currency_id, currency_code, currency_name)
    VALUES (:currency_id, :currency_code, :currency_name)
    ON CONFLICT (currency_id)
    DO UPDATE SET currency_code = EXCLUDED.currency_code, currency_name = EXCLUDED.currency_name;
    """
        assert res == expected

    def test_get_insert_query_not_on_conflict(self):
        table_name = "fact_sales"
        column_names = [
            "sales_record_id",
            "sales_order_id",
            "created_date",
            "created_time",
            "last_updated_date",
            "last_updated_time",
            "sales_staff_id",
            "counterparty_id",
            "units_sold",
            "unit_price",
            "currency_id",
            "design_id",
            "agreed_payment_date",
            "agreed_delivery_date",
            "agreed_delivery_location_id",
        ]
        on_conflict = False
        res = get_insert_query(table_name, column_names, "sales_record_id", on_conflict)
        expected = (
            "INSERT INTO fact_sales (sales_order_id, created_date, created_time, last_updated_date, last_updated_time, sales_staff_id, counterparty_id, units_sold, unit_price, currency_id, design_id, agreed_payment_date, agreed_delivery_date, agreed_delivery_location_id)\n"
            "    VALUES (:sales_order_id, :created_date, :created_time, :last_updated_date, :last_updated_time, :sales_staff_id, :counterparty_id, :units_sold, :unit_price, :currency_id, :design_id, :agreed_payment_date, :agreed_delivery_date, :agreed_delivery_location_id);"
        )
        assert res.strip() == expected.strip()


class TestLoadToDW:
    @patch("src.src_load.load_utils.get_column_names")
    def test_error_logging_load_tables_to_dw(self, mock_get_column_names, caplog):
        mock_get_column_names.side_effect = Exception("cannot get column names")
        with caplog.at_level(logging.CRITICAL):
            load_tables_to_dw("conn", "df", "table_name", "fact_table")
            assert "Unable to load table" in caplog.text

    @patch("src.src_load.load_utils.get_insert_query")
    @patch("src.src_load.load_utils.get_column_names")
    def test_happy_path_logging_info_for_load_tables_to_dw(
        self, mock_get_column_names, mock_get_insert_query, caplog
    ):
        mock_get_column_names.return_value = ["column_a", "column_b", "column_c"]
        mock_get_insert_query.return_value = ""
        conn = Mock()
        conn.run.return_value = ""
        d = {"column_a": [1, 2, 3], "column_b": [2, 3, 4], "column_c": [1, 3, 4]}
        df = pd.DataFrame(d)
        fact_table = []
        with caplog.at_level(logging.INFO):
            load_tables_to_dw(conn, df, "table_name", fact_table)
            assert "loaded 3 rows to table_name" in caplog.text


class TestGetColumnNames:
    def test_loggings_for_database_error_get_column_names(self, caplog):
        conn = Mock()
        conn.run.side_effect = DatabaseError("database error")
        with caplog.at_level(logging.CRITICAL):
            get_column_names(conn, "table_name")
            assert "failed to connect to dw" in caplog.text

    def test_loggings_for_other_errors_get_column_name(self, caplog):
        conn = Mock()
        conn.run.side_effect = InterfaceError("database error")
        with caplog.at_level(logging.CRITICAL):
            get_column_names(conn, "table_name")
            assert "Something goes wrong," in caplog.text
