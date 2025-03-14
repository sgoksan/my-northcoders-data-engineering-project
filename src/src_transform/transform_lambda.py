import os
from botocore.exceptions import ClientError
from datetime import datetime
import sys
import logging

sys.path.append("src/src_transform")
from transform_utils import (
    get_s3_client,
    get_s3_object,
    convert_s3_obj_to_df,
    convert_df_to_s3_obj,
)
from transform_pandas import (
    create_dim_design_table,
    create_dim_currency_table,
    create_dim_staff_table,
    create_dim_location_table,
    create_dim_counterparty_table,
    create_dim_date_table,
    create_fact_sales_order_table,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

INGESTION_BUCKET_NAME = os.environ["S3_BUCKET_NAME_INGESTION"]
PROCESSED_BUCKET_NAME = os.environ["S3_BUCKET_NAME_PROCESSED"]

table_transform_map = {
    "dim_design": (create_dim_design_table, ["design"]),
    "dim_currency": (create_dim_currency_table, ["currency"]),
    "dim_staff": (create_dim_staff_table, ["staff", "department"]),
    "dim_location": (create_dim_location_table, ["address"]),
    "dim_counterparty": (create_dim_counterparty_table, ["address", "counterparty"]),
    "fact_sales_order": (create_fact_sales_order_table, ["sales_order"]),
}


def lambda_handler(event, context):
    """Main handler - This transforms the data from the ingestion s3 bucket, into the
                  required schema for the Data Warehouse, before converting to parquet
                  and putting in processed s3 bucket.
    Args:
          Event: {'department': 'department/20250303131224.json',
                  'transaction': 'transaction/20250303131223.json',
                   'payment': False ...}
                      event is a dictionary that is passed in by StateMachine payload
                      with table names as keys, and object keys as values (False if no new table).
          Context: supplied by AWS


      Exceptions:
      - Exception: General errors within the lambda handler not picked up by exceptions in the utility functions and pandas functions.

      Returns:
      dictionary e.g. {'dim_staff': 'dim_staff/2025-03-03/131224.parquet',
                       'dim_currency': 'dim_currency/2025-03-03/131223.parquet',
                        'dim_staff' : False ...}
      }"""
    try:
        output_event = {
            "dim_design": False,
            "dim_currency": False,
            "dim_staff": False,
            "dim_location": False,
            "dim_counterparty": False,
            "dim_date": False,
            "fact_sales_order": False,
        }
        y_m_d = datetime.now().strftime("%Y-%m-%d")
        filename = datetime.now().strftime("%H%M%S")
        s3_client = get_s3_client()

        for table, (transform_func, event_keys) in table_transform_map.items():
            input_dataframes = []

            if all(event.get(key) for key in event_keys):
                for key in event_keys:
                    obj_key_ingest = event[key]
                    s3_object = get_s3_object(
                        s3_client, INGESTION_BUCKET_NAME, obj_key_ingest
                    )
                    input_dataframes.append(convert_s3_obj_to_df(s3_object))

                df_transformed = transform_func(*input_dataframes)
                obj_key_processed = f"{table}/{y_m_d}/{filename}.parquet"
                output_event[table] = obj_key_processed

                write_result = convert_df_to_s3_obj(
                    s3_client, df_transformed, PROCESSED_BUCKET_NAME, obj_key_processed
                )
                if write_result:
                    logger.info("Wrote %s table to S3", str(table))
                else:
                    logger.info(
                        "There was a problem. %s table not written to S3.", str(table)
                    )

        # dim_date is handled separately as it does not require event input
        df_date = create_dim_date_table()
        obj_key_processed = f"dim_date/{y_m_d}/{filename}.parquet"
        output_event["dim_date"] = obj_key_processed
        write_result = convert_df_to_s3_obj(
            s3_client, df_date, PROCESSED_BUCKET_NAME, obj_key_processed
        )
        if write_result:
            logger.info("Wrote dim_date table to S3")
        else:
            logger.info("There was a problem. dim_date table not written to S3.")
        return output_event

    except Exception as e:
        logger.critical("Unexpected Exception: %s", str(e))
        return output_event
