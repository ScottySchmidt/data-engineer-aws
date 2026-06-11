"""
Part 4 - Reporting Lambda

Improved debug-friendly version of the reporting Lambda.

This Lambda is triggered by SQS after S3 receives a new DataUSA JSON file.
It reads the SQS message, extracts the original S3 event, loads the DataUSA
population JSON file from S3, creates a summary report, and writes the report
to processed/reports/report_summary.json.

This version also prints the raw event for easier debugging and returns a
reports_processed count along with the processed report details so it is easier
to verify that Step 4 successfully ran.
"""

import json
import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ.get("BUCKET_NAME")
PROCESSED_PREFIX = os.environ.get("PROCESSED_PREFIX", "processed/reports/")


def lambda_handler(event, context):
    print("Part 4 reporting Lambda started")
    print("Raw event:")
    print(json.dumps(event))

    processed_reports = []

    for record in event.get("Records", []):
        body = json.loads(record.get("body", "{}"))

        for s3_record in body.get("Records", []):
            source_bucket = s3_record["s3"]["bucket"]["name"]
            source_key = unquote_plus(s3_record["s3"]["object"]["key"])

            print(f"Processing S3 file: s3://{source_bucket}/{source_key}")

            # Read the source DataUSA JSON file from S3
            response = s3.get_object(Bucket=source_bucket, Key=source_key)
            file_content = response["Body"].read().decode("utf-8")
            datausa_json = json.loads(file_content)

            population_rows = datausa_json.get("data", [])

            if population_rows:
                years = [row["Year"] for row in population_rows]
                populations = [row["Population"] for row in population_rows]

                earliest_year = min(years)
                latest_year = max(years)

                earliest_population = next(
                    row["Population"]
                    for row in population_rows
                    if row["Year"] == earliest_year
                )

                latest_population = next(
                    row["Population"]
                    for row in population_rows
                    if row["Year"] == latest_year
                )

                population_change = latest_population - earliest_population

            else:
                earliest_year = None
                latest_year = None
                earliest_population = None
                latest_population = None
                population_change = None

            report = {
                "message": "Part 4 reporting Lambda triggered successfully",
                "source_bucket": source_bucket,
                "source_key": source_key,
                "report_status": "completed",
                "report_created_utc": datetime.now(timezone.utc).isoformat(),
                "dataset_name": datausa_json.get("annotations", {}).get("dataset_name"),
                "source_name": datausa_json.get("annotations", {}).get("source_name"),
                "topic": datausa_json.get("annotations", {}).get("topic"),
                "row_count": len(population_rows),
                "earliest_year": earliest_year,
                "latest_year": latest_year,
                "earliest_population": earliest_population,
                "latest_population": latest_population,
                "population_change": population_change,
            }

            output_bucket = BUCKET_NAME or source_bucket
            output_key = f"{PROCESSED_PREFIX}report_summary.json"

            s3.put_object(
                Bucket=output_bucket,
                Key=output_key,
                Body=json.dumps(report, indent=2).encode("utf-8"),
                ContentType="application/json",
            )

            print(f"Wrote report output to s3://{output_bucket}/{output_key}")

            processed_reports.append(report)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Reporting Lambda complete",
                "reports_processed": len(processed_reports),
                "processed_reports": processed_reports,
            }
        ),
    }
