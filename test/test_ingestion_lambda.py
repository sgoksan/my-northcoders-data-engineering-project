import pytest
from moto import mock_aws
import boto3
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from freezegun import freeze_time
from unittest.mock import patch, Mock
import sys

sys.path.append("src/src_ingestion")

with patch.dict(os.environ, {"S3_BUCKET_NAME": "test_bucket_ingestion"}):
    from src.src_ingestion.ingestion_lambda import lambda_handler


class DummyContext:
    pass


class DummyEvent:
    pass


@pytest.fixture(scope="function")
def mock_conn_test():
    mock_conn = Mock()
    mock_conn.run.return_value = [
        1,
        "Jeremie",
        "Franey",
        2,
        "email",
        "2022-11-03 14:20:49.962000",
    ]
    mock_conn.columns = [
        {"name": "id"},
        {"name": "first_name"},
        {"name": "last_name"},
        {"name": "department_id"},
        {"name": "email"},
        {"name": "last_updated"},
    ]
    return mock_conn


@pytest.fixture(scope="function")
def mock_conn_test_2():
    mock_conn = Mock()
    mock_conn.run.return_value = [
        1,
        "file/image/tote",
        "image.png",
        "2022-11-03 14:20:49.962000",
    ]
    mock_conn.columns = [
        {"name": "design_id"},
        {"name": "filepath"},
        {"name": "filename"},
        {"name": "last_updated"},
    ]
    return mock_conn


@pytest.fixture(scope="function")
def s3_client():
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(Bucket="test_bucket_ingestion")
        yield client


@patch("src.src_ingestion.ingestion_lambda.connect_to_db")
@patch("src.src_ingestion.ingestion_lambda.fetch_latest_update_time_from_db")
@patch("src.src_ingestion.ingestion_lambda.fetch_latest_update_time_from_s3")
@freeze_time("2025-03-05 12:00")
def test_ingest_handler_writes_objects_to_s3(
    mock_fetch_s3, mock_fetch_db, mock_conn_func, s3_client, mock_conn_test, caplog
):

    context = DummyContext()
    event = DummyEvent()
    with mock_aws():
        mock_conn_func.run.return_value = mock_conn_test
        mock_fetch_s3.return_value = 20000101000001
        mock_fetch_db.return_value = 20250302140516
        with caplog.at_level(logging.INFO):
            lambda_handler(event, context)
            bucket_data = s3_client.list_objects_v2(Bucket="test_bucket_ingestion")
            assert bucket_data["KeyCount"] == 11
            assert "Wrote address table to S3" in caplog.text


@patch("src.src_ingestion.ingestion_lambda.connect_to_db")
@patch("src.src_ingestion.ingestion_lambda.fetch_latest_update_time_from_s3")
def test_ingest_handler_handles_unexpected_exception(
    mock_fetch_s3, mock_conn_func, caplog
):
    with mock_aws():
        mock_fetch_s3.side_effect = TypeError
        mock_conn_func.run.return_value = mock_conn_test
        context = DummyContext()
        event = DummyEvent()
        with caplog.at_level(logging.INFO):
            lambda_handler(event, context)
            assert "Unexpected Exception" in caplog.text


@patch("src.src_ingestion.ingestion_lambda.connect_to_db")
@patch("src.src_ingestion.ingestion_lambda.fetch_latest_update_time_from_db")
@patch("src.src_ingestion.ingestion_lambda.fetch_latest_update_time_from_s3")
@patch("src.src_ingestion.ingestion_lambda.upload_to_s3")
def test_ingest_handler_handles_client_error(
    mock_upload_s3, mock_fetch_s3, mock_fetch_db, mock_conn_func, caplog
):
    with mock_aws():
        mock_upload_s3.return_value = None
        mock_fetch_s3.return_value = 20000101000001
        mock_fetch_db.return_value = 20250302140516
        mock_conn_func.run.return_value = mock_conn_test
        context = DummyContext()
        event = DummyEvent()
        with caplog.at_level(logging.INFO):
            lambda_handler(event, context)
            assert "There was a problem" in caplog.text
