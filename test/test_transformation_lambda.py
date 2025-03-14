import pytest
from moto import mock_aws
import boto3
import os
import logging
from freezegun import freeze_time
from unittest.mock import patch

with patch.dict(
    os.environ,
    {
        "S3_BUCKET_NAME_INGESTION": "test_bucket_ingestion",
        "S3_BUCKET_NAME_PROCESSED": "test_bucket_processed",
    },
):
    from src.src_transform.transform_lambda import lambda_handler


class DummyContext:
    pass


@pytest.fixture(scope="function")
def lambda_event():
    return {
        "department": "department/2025-03-01/071556.json",
        "transaction": False,
        "payment": False,
        "design": "design/2025-03-03/131223.json",
        "address": False,
        "staff": False,
        "counterparty": False,
        "currency": False,
        "sales_order": False,
    }


@freeze_time("2024-04-01 12:00")
def test_handler_writes_objects_to_s3(
    lambda_event,
    s3_client,
    create_bucket,
    create_object_design,
    bucket_name,
    object_key_design,
    bucket_name_processed,
    create_bucket_processed,
    create_object,
    caplog,
):
    with mock_aws():
        context = DummyContext()
        with caplog.at_level(logging.INFO):
            lambda_handler(lambda_event, context)
            bucket_data = s3_client.list_objects_v2(Bucket="test_bucket_processed")
            assert bucket_data["KeyCount"] == 2
            assert (
                bucket_data["Contents"][0]["Key"]
                == "dim_date/2024-04-01/120000.parquet"
            )
            assert (
                bucket_data["Contents"][1]["Key"]
                == "dim_design/2024-04-01/120000.parquet"
            )
            assert "Wrote dim_design table to S3" in caplog.text
            assert "Wrote dim_date table to S3" in caplog.text


@patch("src.src_transform.transform_lambda.convert_df_to_s3_obj")
@freeze_time("2024-04-01 12:00")
def test_handler_handles_client_error(
    mock_convert_s3,
    lambda_event,
    s3_client,
    create_bucket,
    bucket_name,
    object_key_design,
    bucket_name_processed,
    create_bucket_processed,
    caplog,
):
    with mock_aws():
        mock_convert_s3.return_value = False
        context = DummyContext()
        with caplog.at_level(logging.INFO):
            lambda_handler(lambda_event, context)
            assert "There was a problem. dim_design table not written" in caplog.text
            assert "There was a problem. dim_date table not written" in caplog.text


@patch("src.src_transform.transform_lambda.convert_df_to_s3_obj")
@freeze_time("2024-04-01 12:00")
def test_handler_handles_unexpected_exception(mock_convert_s3, lambda_event, caplog):
    with mock_aws():
        mock_convert_s3.side_effect = TypeError
        context = DummyContext()
        with caplog.at_level(logging.CRITICAL):
            lambda_handler(lambda_event, context)
            assert "Unexpected Exception" in caplog.text
