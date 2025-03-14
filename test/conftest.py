import pytest
from moto import mock_aws
import boto3
import os
import json
import pandas as pd


@pytest.fixture(scope="function", autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture()
def s3_client():
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-2")


@pytest.fixture()
def bucket_name():
    return "test_bucket_ingestion"


@pytest.fixture()
def bucket_name_processed():
    return "test_bucket_processed"


@pytest.fixture
def create_bucket(s3_client, bucket_name):
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )


@pytest.fixture
def create_bucket_processed(s3_client, bucket_name_processed):
    s3_client.create_bucket(
        Bucket=bucket_name_processed,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )


@pytest.fixture()
def object_key():
    return "department/2025-03-01/071556.json"


@pytest.fixture()
def object_body():
    return {
        "columns": [
            "department_id",
            "department_name",
            "location",
            "manager",
            "created_at",
            "last_updated",
        ],
        "data": [
            [
                1,
                "Sales",
                "Manchester",
                "Richard Roma",
                "2022-11-03 14:20:49.962000",
                "2022-11-03 14:20:49.962000",
            ],
            [
                2,
                "Purchasing",
                "Manchester",
                "Naomi Lapaglia",
                "2022-11-03 14:20:49.962000",
                "2022-11-03 14:20:49.962000",
            ],
            [
                3,
                "Production",
                "Leeds",
                "Chester Ming",
                "2022-11-03 14:20:49.962000",
                "2022-11-03 14:20:49.962000",
            ],
        ],
    }


@pytest.fixture
def create_object(s3_client, bucket_name, object_key, object_body):
    obj_json = json.dumps(object_body, indent=4, sort_keys=True, default=str)
    obj_bytes = obj_json.encode("utf-8")
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=obj_bytes)


@pytest.fixture()
def object_key_design():
    return "design/2025-03-03/131223.json"


@pytest.fixture()
def object_body_design():
    return {
        "columns": [
            "design_id",
            "created_at",
            "design_name",
            "file_location",
            "file_name",
            "last_updated",
        ],
        "data": [
            [
                8,
                "2022-11-03 14:20:49.962000",
                "Wooden",
                "/usr",
                "wooden-20220717-npgz.json",
                "2022-11-03 14:20:49.962000",
            ],
            [
                51,
                "2023-01-12 18:50:09.935000",
                "Bronze",
                "/private",
                "bronze-20221024-4dds.json",
                "2023-01-12 18:50:09.935000",
            ],
            [
                69,
                "2023-02-07 17:31:10.093000",
                "Bronze",
                "/lost+found",
                "bronze-20230102-r904.json",
                "2023-02-07 17:31:10.093000",
            ],
        ],
    }


@pytest.fixture()
def create_object_design(s3_client, bucket_name, object_key_design, object_body_design):
    obj_json = json.dumps(object_body_design, indent=4, sort_keys=True, default=str)
    obj_bytes = obj_json.encode("utf-8")
    s3_client.put_object(Bucket=bucket_name, Key=object_key_design, Body=obj_bytes)


@pytest.fixture(scope="module")
def input_data_design():
    data = {
        "design_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "design_name": ["design1", "design2", "design3"],
        "file_location": ["folder/next", "folder2/next2", "folder3/next3"],
        "file_name": ["image.png", "image2.png", "image2.png"],
    }

    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def output_data_design():
    data = {
        "design_id": [1, 2, 3],
        "design_name": ["design1", "design2", "design3"],
        "file_location": ["folder/next", "folder2/next2", "folder3/next3"],
        "file_name": ["image.png", "image2.png", "image2.png"],
    }
    return pd.DataFrame(data=data).set_index("design_id")


@pytest.fixture(scope="module")
def input_data_currency():
    data = {
        "currency_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "currency_code": ["GBP", "EUR", "USD"],
    }
    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def output_data_currency():
    data = {
        "currency_id": [1, 2, 3],
        "currency_code": ["GBP", "EUR", "USD"],
        "currency_name": ["Pound sterling", "Euro", "United States dollar"],
    }
    return pd.DataFrame(data=data).set_index("currency_id")


@pytest.fixture(scope="module")
def input_data_staff():
    data = {
        "staff_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "first_name": ["Tom", "Sam", "John"],
        "last_name": ["Jones", "Wilde", "Smith"],
        "department_id": [1, 2, 3],
        "email_address": ["tom@totebags.com", "sam@totebags.com", "john@totebags.com"],
    }
    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def input_data_department():
    data = {
        "department_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "department_name": ["Sales", "Tech", "Marketing"],
        "location": ["Manchester", "London", "Leeds"],
        "manager": ["Paul C.", "Eli S.", "Danika R."],
    }
    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def output_data_staff():
    data = {
        "staff_id": [1, 2, 3],
        "first_name": ["Tom", "Sam", "John"],
        "last_name": ["Jones", "Wilde", "Smith"],
        "email_address": ["tom@totebags.com", "sam@totebags.com", "john@totebags.com"],
        "department_name": ["Sales", "Tech", "Marketing"],
        "location": ["Manchester", "London", "Leeds"],
    }
    return pd.DataFrame(data=data).set_index("staff_id")


@pytest.fixture(scope="module")
def input_data_address():
    data = {
        "address_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "address_line_1": ["3 Church Lane", "10 Nelson Road", "4 Wilton Avenue"],
        "address_line_2": ["Putney", "Camden", "Kew"],
        "district": ["Lambeth", "Merton", "Richmond"],
        "city": ["Manchester", "London", "Leeds"],
        "postal_code": ["GU1 342", "TW3 827", "YE4 978"],
        "phone": ["078853686554", "07576455456", "07846556544"],
    }
    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def output_data_location():
    data = {
        "location_id": [1, 2, 3],
        "address_line_1": ["3 Church Lane", "10 Nelson Road", "4 Wilton Avenue"],
        "address_line_2": ["Putney", "Camden", "Kew"],
        "district": ["Lambeth", "Merton", "Richmond"],
        "city": ["Manchester", "London", "Leeds"],
        "postal_code": ["GU1 342", "TW3 827", "YE4 978"],
        "phone": ["078853686554", "07576455456", "07846556544"],
    }
    return pd.DataFrame(data=data).set_index("location_id")


@pytest.fixture(scope="module")
def input_data_counterparty():
    data = {
        "counterparty_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "counterparty_legal_name": ["Paul C.", "Eli S.", "Danika R."],
        "legal_address_id": [1, 2, 3],
        "commercial_contact": ["Argos", "WH Smiths", "Homebase"],
        "delivery_contact": ["Warehouse", "Logistics", "Supply Chains"],
    }
    return pd.DataFrame(data=data)


@pytest.fixture(scope="module")
def output_data_counterparty():
    data = {
        "counterparty_id": [1, 2, 3],
        "counterparty_legal_name": ["Paul C.", "Eli S.", "Danika R."],
        "counterparty_legal_address_line_1": [
            "3 Church Lane",
            "10 Nelson Road",
            "4 Wilton Avenue",
        ],
        "counterparty_legal_address_line_2": ["Putney", "Camden", "Kew"],
        "counterparty_legal_district": ["Lambeth", "Merton", "Richmond"],
        "counterparty_legal_city": ["Manchester", "London", "Leeds"],
        "counterparty_legal_postal_code": ["GU1 342", "TW3 827", "YE4 978"],
        "counterparty_legal_phone_number": [
            "078853686554",
            "07576455456",
            "07846556544",
        ],
    }
    return pd.DataFrame(data=data).set_index("counterparty_id")


@pytest.fixture(scope="module")
def output_data_date():
    data = {
        "date_id": ["2025-03-03", "2025-03-04", "2025-03-05"],
        "year": [2025, 2025, 2025],
        "month": [3, 3, 3],
        "day": [3, 4, 5],
        "day_of_week": [1, 2, 3],
        "day_name": ["Monday", "Tuesday", "Wednesday"],
        "month_name": ["March", "March", "March"],
        "quarter": [1, 1, 1],
    }
    df_date = pd.DataFrame(data=data).set_index("date_id")

    return df_date


# sales_order_id last updated date and time


@pytest.fixture(scope="module")
def input_data_sales_order():
    data = {
        "sales_order_id": [1, 2, 3],
        "created_at": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "last_updated": [
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
            "2022-11-03 14:20:49.962000",
        ],
        "design_id": [1, 2, 3],
        "staff_id": [1, 2, 3],
        "counterparty_id": [1, 2, 3],
        "units_sold": [12345, 53422134, 9873234567],
        "unit_price": [12.34, 5.32, 9.99],
        "currency_id": [1, 2, 3],
        "agreed_delivery_date": ["2025-01-18", "4032-01-08", "2024-12-22"],
        "agreed_payment_date": ["2025-01-18", "4032-01-08", "2024-12-22"],
        "agreed_delivery_location_id": [2345, 2, 5],
    }
    df_sales_order = pd.DataFrame(data=data)

    return df_sales_order


@pytest.fixture(scope="module")
def output_data_sales_order():
    data = {
        "sales_order_id": [1, 2, 3],
        "design_id": [1, 2, 3],
        "sales_staff_id": [1, 2, 3],
        "counterparty_id": [1, 2, 3],
        "units_sold": [12345, 53422134, 9873234567],
        "unit_price": [12.34, 5.32, 9.99],
        "currency_id": [1, 2, 3],
        "agreed_delivery_date": ["2025-01-18", "4032-01-08", "2024-12-22"],
        "agreed_payment_date": ["2025-01-18", "4032-01-08", "2024-12-22"],
        "agreed_delivery_location_id": [2345, 2, 5],
        "created_date": ["2022-11-03", "2022-11-03", "2022-11-03"],
        "created_time": ["14:20:49.962000", "14:20:49.962000", "14:20:49.962000"],
        "last_updated_date": ["2022-11-03", "2022-11-03", "2022-11-03"],
        "last_updated_time": ["14:20:49.962000", "14:20:49.962000", "14:20:49.962000"],
    }
    output_df_sales_order = pd.DataFrame(data=data).set_index("sales_order_id")
    return output_df_sales_order
