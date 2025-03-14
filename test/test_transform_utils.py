from moto import mock_aws
import boto3
from src.src_transform.transform_utils import (
    get_s3_object,
    convert_s3_obj_to_df,
    convert_df_to_s3_obj,
)
import logging
import pandas as pd


class TestGetS3Object:

    def test_get_s3_object_can_access_files_as_dict(
        self, s3_client, create_bucket, create_object, bucket_name, object_key
    ):
        with mock_aws():
            response = get_s3_object(s3_client, bucket_name, object_key)
            assert isinstance(response, dict)
            assert "columns" in response
            assert "data" in response

    def test_get_s3_object_creates_dict_with_correct_schema(
        self, s3_client, create_bucket, create_object, bucket_name, object_key
    ):
        with mock_aws():
            response = get_s3_object(s3_client, bucket_name, object_key)
            assert "department_id" in response["columns"]
            assert len(response["columns"]) is 6
            assert "Sales" in response["data"][0]
            assert len(response["data"][0]) is 6
            assert isinstance(response["data"][0][0], int)

    def test_get_s3_object_logging(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "test-bucket"
            filename = "table"
            result = {"key": "value"}
            with caplog.at_level(logging.CRITICAL):
                get_s3_object(client, bucket_name, filename)
                assert "Unable to get object from Ingestion Bucket" in caplog.text


class TestConvertS3ToDF:

    def test_convert_s3_obj_to_df_can_create_df(
        self, s3_client, bucket_name, object_key, create_bucket, create_object
    ):
        with mock_aws():
            s3_obj = get_s3_object(s3_client, bucket_name, object_key)
            response = convert_s3_obj_to_df(s3_obj)
            assert isinstance(response, object)
            assert len(response) is 3
            assert "department_id" in response
            assert "department_name" in response
            assert "location" in response
            assert "manager" in response

    def test_convert_s3_obj_to_df_key_error_logging(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            fake_s3_obj_dict = {"key": "value"}
            with caplog.at_level(logging.ERROR):
                convert_s3_obj_to_df(fake_s3_obj_dict)
                assert (
                    "Key Error when converting s3 object to panda data frame"
                    in caplog.text
                )

    def test_convert_s3_obj_to_df_type_error_logging(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            fake_s3_obj_dict = {"data": "columns"}
            with caplog.at_level(logging.ERROR):
                convert_s3_obj_to_df(1)
                assert (
                    "Type Error when converting s3 object to panda data frame"
                    in caplog.text
                )

    def test_convert_s3_obj_to_df_exception_logging(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            fake_s3_obj_dict = {"data": "any data", "columns": "any columns"}
            with caplog.at_level(logging.CRITICAL):
                convert_s3_obj_to_df(fake_s3_obj_dict)
                assert (
                    "Error when converting s3 object to panda data frame" in caplog.text
                )


class TestConvertDFToS3:

    def test_convert_df_to_s3_object(
        self,
        s3_client,
        bucket_name,
        object_key,
        create_bucket,
        create_object,
        bucket_name_processed,
    ):
        with mock_aws():
            s3_obj = get_s3_object(s3_client, bucket_name, object_key)
            df = convert_s3_obj_to_df(s3_obj)
            convert_df_to_s3_obj(s3_client, df, bucket_name, object_key)
            listing = s3_client.list_objects_v2(Bucket=bucket_name)
            assert len(listing["Contents"]) == 1
            assert listing["Contents"][0]["Key"] == object_key

    def test_convert_s3_obj_to_df_client_error_logging(self, caplog):
        with mock_aws():
            client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "test-bucket"
            filename = "table"
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            with caplog.at_level(logging.ERROR):
                convert_df_to_s3_obj(client, df, bucket_name, filename)
                assert (
                    "S3 Client Error when converting panda dataframe to s3 object"
                    in caplog.text
                )

    def test_convert_s3_obj_to_df_exception_error_logging(self, caplog):
        with mock_aws():
            client = "S3"
            bucket_name = "test-bucket"
            filename = "table"
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            with caplog.at_level(logging.CRITICAL):
                convert_df_to_s3_obj(client, df, bucket_name, filename)
                assert (
                    "Error when converting panda data frame to s3 object" in caplog.text
                )
