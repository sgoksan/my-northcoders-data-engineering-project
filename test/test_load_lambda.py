from moto import mock_aws
from unittest.mock import patch, Mock
import logging, pytest, os
from io import BytesIO


class DummyContext:
    pass


with patch.dict(os.environ, {"S3_BUCKET_NAME_PROCESSED": "test_bucket_processed"}):
    from src.src_load.load_lambda import lambda_handler


@pytest.fixture(scope="function")
def lambda_event():
    return {
        "dim_design": "dim_design/2025-03-06/224349.parquet",
        "dim_currency": False,
        "dim_staff": "dim_staff/2025-03-06/224349.parquet",
        "dim_location": "dim_location/2025-03-06/224349.parquet",
        "dim_counterparty": "dim_counterparty/2025-03-06/224349.parquet",
        "dim_date": "dim_date/2025-03-06/224349.parquet",
        "fact_sales_order": "fact_sales_order/2025-03-06/224349.parquet",
    }


@pytest.fixture(scope="function")
def lambda_event_2():
    return {
        "dim_design": "dim_design/2025-03-06/224349.parquet",
        "dim_currency": False,
        "dim_staff": False,
        "dim_location": False,
        "dim_counterparty": False,
        "dim_date": False,
        "fact_sales_order": False,
    }


@pytest.fixture()
def object_key_dim_design():
    return "dim_design/2025-03-06/224349.parquet"


@pytest.fixture
def create_dim_design_object(
    s3_client, bucket_name_processed, object_key_dim_design, output_data_design
):
    output_buffer = BytesIO()
    output_data_design.to_parquet(output_buffer)
    body = output_buffer.getvalue()
    s3_client.put_object(
        Bucket=bucket_name_processed, Key=object_key_dim_design, Body=body
    )


@patch("src.src_load.load_lambda.connect_to_dw")
def test_load_lambda_successfully_loads_tables(
    mock_conn_dw,
    bucket_name_processed,
    create_bucket_processed,
    create_dim_design_object,
    lambda_event_2,
    caplog,
):
    with mock_aws():
        context = DummyContext()
        mock_conn_dw.run.return_value = Mock()
        with caplog.at_level(logging.INFO):
            lambda_handler(lambda_event_2, context, BUCKET_NAME=bucket_name_processed)
            assert "dim_design loaded successfully" in caplog.text
            assert "loaded 3 rows to dim_design" in caplog.text


@patch("src.src_load.load_lambda.get_s3_client")
def test_logging_for_lambda_handler(
    mock_get_s3_client, lambda_event, bucket_name_processed, caplog
):
    with mock_aws():
        mock_get_s3_client.side_effect = Exception("Something is wrong")
        context = DummyContext()
        with caplog.at_level(logging.CRITICAL):
            lambda_handler(lambda_event, context, BUCKET_NAME=bucket_name_processed)
            assert "Unexpected Exception" in caplog.text
