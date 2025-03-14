import os
import logging
from datetime import datetime
from pg8000.native import identifier
from utils import (
    upload_to_s3,
    get_s3_client,
    fetch_latest_update_time_from_s3,
    fetch_latest_update_time_from_db,
    connect_to_db,
    close_db_connection,
    fetch_snapshot_of_table_from_db,
)
import sys

sys.path.append("src/src_ingestion")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def lambda_handler(event, context, BUCKET_NAME=BUCKET_NAME):
    """Ingestion Lambda to put the latest data from ToteSys in the ingestion_zone_S3 bucket.

    Input Arguments:
    - event: trigger provided by AWS step machine
    - context: supplied by AWS
    - BUCKET_NAME = The S3 Bucket Name that the handler will write to.
        - Defaults to the available ENVIRONMENT VARIABLE: "S3_BUCKET_NAME".

    Returned Output:
    Output dictionary with 11 key-value pairs:
        - Each Key is the name of the Table being ingested from ToteSys DB.
        - Each Value is either:
            (a) the filepath to the latest object that was written to s3 during the last fetch.
            (b) False: if no new file was uploaded during the last fetch.

    This lambda will SELECT data from the ToteSys Database and:
    For each table in the database, it will:
        - load the data in to a dictionary with two keys:
            "columns" : <list of table headers>
            "data" : <contains raw data as a list of lists. Each list is one row of the table.>
        - opens a temporary file in lambda's /tmp dir and dumps the data there in json format
        - uploads that file object to the s3 bucket using the following format:
            - table_name/year-month-day-timestamp.json (i.e. YYYYMMDDHHMMSS.json)
        - finally this lambda will close the db conn.

    Exceptions:
    - Exception: General errors within the lambda handler not picked up by exceptions in the utility functions.

    Important Notes:
        - Any data in a datetime format when extracted from ToteSys is coverted in to a integer format.
        - Within the uploaded file: any data fields that had None have been converted to 'null' values.
    """
    conn = None
    output = {}
    try:
        conn = connect_to_db()
        client = get_s3_client()
        table_list = [
            "design",
            "transaction",
            "sales_order",
            "address",
            "counterparty",
            "staff",
            "purchase_order",
            "payment",
            "payment_type",
            "currency",
            "department",
        ]
        for table in table_list:
            latest_update_s3 = fetch_latest_update_time_from_s3(
                client, BUCKET_NAME, table
            )
            latest_update_db = fetch_latest_update_time_from_db(conn, table)
            if latest_update_db > latest_update_s3:
                latest_update_s3_dt = datetime.strptime(
                    str(latest_update_s3), "%Y%m%d%H%M%S"
                )
                raw_data = conn.run(
                    f"SELECT * FROM {identifier(table)} WHERE last_updated > :latest_update_s3_dt",
                    latest_update_s3_dt=latest_update_s3_dt,
                )
                columns = [col["name"] for col in conn.columns]
                result = {"columns": columns, "data": raw_data}
                object_name = upload_to_s3(BUCKET_NAME, table, result, client)
                if object_name:
                    output[table] = object_name
                    logger.info("Wrote %s table to S3", str(table))
                else:
                    logger.info(
                        "There was a problem. %s table not written to S3.", str(table)
                    )
            else:
                output[table] = False

        # Fetch full snapshot for cases where a table in DW needs a join, so it needs data from its counterpart table
        table_joins_lookup = {
            "staff": "department",
            "department": "staff",
            "counterparty": "address",
            "address": "counterparty",
        }
        list_tables_needed = [
            value for key, value in table_joins_lookup.items() if output[key]
        ]

        for table_name in list_tables_needed:
            result = fetch_snapshot_of_table_from_db(conn, table_name)
            object_name = upload_to_s3(BUCKET_NAME, table_name, result, client)
            if object_name:
                output[table_name] = object_name
                logger.info("Wrote %s table to S3", str(table_name))
            else:
                logger.info(
                    "There was a problem. %s table not written to S3.", str(table_name)
                )

        close_db_connection(conn)
        return output
    except Exception as e:
        logger.info("Unexpected Exception: %s", str(e))
        return output
    finally:
        if conn:
            close_db_connection(conn)
