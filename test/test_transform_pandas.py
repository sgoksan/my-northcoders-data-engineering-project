import pytest
import pandas as pd
from src.src_transform.transform_pandas import (
    create_dim_design_table,
    create_dim_currency_table,
    create_dim_staff_table,
    create_dim_location_table,
    create_dim_counterparty_table,
    create_dim_date_table,
    create_fact_sales_order_table,
)
from moto import mock_aws
import boto3
import logging


class TestDimDesign:
    def test_create_dim_design_creates_correct_schema(
        self, input_data_design, output_data_design
    ):
        dim_design_data = create_dim_design_table(input_data_design)
        pd.testing.assert_frame_equal(dim_design_data, output_data_design)

    def test_create_dim_design_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.ERROR):
                create_dim_design_table(df)
                assert "Key Error, unable to create dim_design table" in caplog.text

    def test_create_dim_design_table_exception_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.CRITICAL):
                create_dim_design_table("test-string")
                assert "Error Unable to create dim_design table" in caplog.text


class TestDimCurrency:
    def test_create_dim_currency_creates_correct_schema(
        self, input_data_currency, output_data_currency
    ):
        dim_currency_data = create_dim_currency_table(input_data_currency)
        pd.testing.assert_frame_equal(dim_currency_data, output_data_currency)

    def test_create_dim_currency_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.ERROR):
                create_dim_currency_table(df)
                assert "Key Error, unable to create dim_curruncy table" in caplog.text

    def test_create_dim_curency_table_exception_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.CRITICAL):
                create_dim_currency_table("test-string")
                assert "Error, Unable to create dim_curruncy table" in caplog.text


class TestDimStaff:
    def test_create_dim_staff_creates_correct_schema(
        self, input_data_staff, input_data_department, output_data_staff
    ):
        dim_staff_data = create_dim_staff_table(input_data_staff, input_data_department)
        pd.testing.assert_frame_equal(dim_staff_data, output_data_staff)

    def test_create_dim_curency_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            data_2 = {"calories_2": [100, 200, 30], "duration_2": [1, 2, 3]}
            df2 = pd.DataFrame(data_2)
            with caplog.at_level(logging.ERROR):
                create_dim_staff_table(df, df2)
                assert "Key Error, Unable to create dim_staff table" in caplog.text

    def test_create_dim_staff_table_exception_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.CRITICAL):
                create_dim_staff_table("test_string_1", "test_string_2")
                assert "Error, unable to create dim_staff table" in caplog.text


class TestDimLocation:
    def test_create_dim_location_creates_correct_schema(
        self, input_data_address, output_data_location
    ):
        dim_location_data = create_dim_location_table(input_data_address)
        pd.testing.assert_frame_equal(dim_location_data, output_data_location)

    def test_create_dim_location_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            with caplog.at_level(logging.ERROR):
                create_dim_location_table(df)
                assert "Key Error, unable to create dim_location table" in caplog.text

    def test_create_dim_location_table_exception_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.CRITICAL):
                create_dim_location_table("test_string_1")
                assert "Error, unable to create dim_location table" in caplog.text


class TestDimCounterparty:
    def test_create_dim_counterparty_creates_correct_schema(
        self, input_data_address, input_data_counterparty, output_data_counterparty
    ):
        dim_counterparty_data = create_dim_counterparty_table(
            input_data_address, input_data_counterparty
        )
        pd.testing.assert_frame_equal(dim_counterparty_data, output_data_counterparty)

    def test_create_dim_counterparty_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            data_2 = {"calories_2": [100, 200, 30], "duration_2": [1, 2, 3]}
            df2 = pd.DataFrame(data_2)

            with caplog.at_level(logging.ERROR):
                create_dim_counterparty_table(df, df2)
                assert (
                    "Key Error, unable to create dim_counter_party table" in caplog.text
                )

    def test_create_dim_counterparty_table_exception_error_logging(self, caplog):
        with mock_aws():
            test_obj_1 = {"key-1": "test-key-1"}
            test_obj_2 = {"key-2": "test-key-2"}
            with caplog.at_level(logging.CRITICAL):
                create_dim_counterparty_table(test_obj_1, test_obj_2)
                assert "Error, unable to create dim_counter_party table" in caplog.text


class TestDimDate:
    def test_create_dim_date_creates_correct_schema(self, output_data_date):
        dim_date_data = create_dim_date_table(start="2025/03/03", end="2025/03/05")
        pd.testing.assert_frame_equal(
            dim_date_data, output_data_date, check_dtype=False
        )

    def test_create_dim_date_table_value_error_logging(self, caplog):
        with mock_aws():

            with caplog.at_level(logging.ERROR):
                create_dim_date_table("start_date", "end_date")
                assert "Value Error, unable to create dim_date table" in caplog.text

    def test_create_dim_date_table_exception_error_logging(self, caplog):
        with mock_aws():

            with caplog.at_level(logging.ERROR):
                create_dim_date_table(1, 1)
                assert "Error, unable to create dim_date table" in caplog.text


class TestFactSalesOrder:
    def test_create_fact_sales_order(
        self, input_data_sales_order, output_data_sales_order
    ):
        fact_sales_order_data = create_fact_sales_order_table(input_data_sales_order)
        pd.testing.assert_frame_equal(fact_sales_order_data, output_data_sales_order)

    def test_create_fact_sales_order_table_key_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)

            with caplog.at_level(logging.ERROR):
                create_fact_sales_order_table(df)
                assert (
                    "Key Error, unable to create fact_sales_order table" in caplog.text
                )

    def test_create_fact_sales_order_table_exception_error_logging(self, caplog):
        with mock_aws():
            data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
            df = pd.DataFrame(data)
            with caplog.at_level(logging.CRITICAL):
                create_fact_sales_order_table("test_string_1")
                assert "Error, unable to create fact_sales_order table" in caplog.text
