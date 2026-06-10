"""
Part 4 - Reporting Lambda

This Lambda is triggered by SQS after S3 receives a new DataUSA JSON file.
It reads the S3 event message, logs the source file, and writes a simple
report output to the processed/reports/ folder.
"""

import json
import os

import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME")
PROCESSED_PREFIX = os.environ.get("PROCESSED_PREFIX", "processed/reports/")


def lambda_handler(event, context):
    print("Part 4 reporting Lambda started")
    print("Raw event:")
    print(json.dumps(event))

    processed_records = []

    for record in event.get("Records", []):
        body = json.loads(record.get("body", "{}"))

        for s3_record in body.get("Records", []):
            source_bucket = s3_record["s3"]["bucket"]["name"]
            source_key = s3_record["s3"]["object"]["key"]

            print(f"Processing S3 file: s3://{source_bucket}/{source_key}")

            report = {
                "message": "Part 3 reporting Lambda triggered successfully",
                "source_bucket": source_bucket,
                "source_key": source_key,
                "report_status": "completed",
            }

            output_key = f"{PROCESSED_PREFIX}report_summary.json"

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=output_key,
                Body=json.dumps(report, indent=2).encode("utf-8"),
                ContentType="application/json",
            )

            print(f"Wrote report output to s3://{BUCKET_NAME}/{output_key}")
            processed_records.append(report)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Reporting Lambda complete",
                "records_processed": len(processed_records),
                "records": processed_records,
            }
        ),
    }