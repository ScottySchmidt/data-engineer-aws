"""
Part 4 - Combined AWS Lambda Ingest

This Lambda combines the Part 1 BLS ingest process and the Part 2 DataUSA
ingest process into one scheduled function.

Part 1: Fetches BLS time series data and stores it in S3.
Part 2: Fetches DataUSA population data and stores it in S3.

This combined Lambda is intended to be triggered automatically by EventBridge
as part of the automated AWS data pipeline.
"""

import hashlib
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List

import boto3


s3 = boto3.client("s3")

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
DEFAULT_BLS_PREFIX = "raw/bls/api/"


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def parse_series_ids(series_ids_raw: str) -> List[str]:
    series_ids = [s.strip() for s in series_ids_raw.split(",") if s.strip()]

    if not series_ids:
        raise ValueError("SERIES_IDS must contain at least one BLS series ID.")

    return series_ids


def fetch_bls_data(series_ids: List[str], api_key: str) -> Dict[str, Any]:
    payload = {
        "seriesid": series_ids,
        "registrationkey": api_key,
    }

    body = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": os.environ.get("USER_AGENT", "ScottSchmidt/1.0"),
    }

    request = urllib.request.Request(
        BLS_API_URL,
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
            status_code = response.getcode()

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"BLS API error {exc.code}: {error_body[:500]}") from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(f"BLS API request failed: {exc}") from exc

    if status_code != 200:
        raise RuntimeError(f"BLS API error {status_code}: {response_body[:500]}")

    data = json.loads(response_body)

    if data.get("status") not in (None, "REQUEST_SUCCEEDED"):
        raise RuntimeError(f"BLS API returned unsuccessful status: {data}")

    return data


def build_bls_s3_key(series_ids: List[str], bls_prefix: str) -> str:
    filename = f"bls_{'-'.join(sorted(series_ids))}.json"
    return f"{bls_prefix.rstrip('/')}/{filename}"


def upload_if_changed(bucket_name: str, s3_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(data, indent=2, sort_keys=True)
    body_hash = hashlib.md5(body.encode("utf-8")).hexdigest()

    try:
        existing = s3.head_object(Bucket=bucket_name, Key=s3_key)
        existing_hash = existing.get("Metadata", {}).get("content-md5")

        if not existing_hash:
            existing_hash = existing.get("ETag", "").strip('"')

    except Exception:
        existing_hash = None

    if existing_hash == body_hash:
        print(f"No changes; skipped upload: {s3_key}")

        return {
            "uploaded": False,
            "s3_key": s3_key,
            "content_md5": body_hash,
            "message": "No changes; skipped upload.",
        }

    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
        Metadata={"content-md5": body_hash},
    )

    print(f"Uploaded to S3: {s3_key}")

    return {
        "uploaded": True,
        "s3_key": s3_key,
        "content_md5": body_hash,
        "message": "Uploaded new or changed file.",
    }


def ingest_bls(bucket_name: str) -> Dict[str, Any]:
    """
    Part 1: BLS ingest
    """
    print("Part 1 BLS ingest started")

    api_key = get_required_env("BLS_API_KEY")
    series_ids = parse_series_ids(get_required_env("SERIES_IDS"))
    bls_prefix = os.environ.get("BLS_PREFIX", DEFAULT_BLS_PREFIX).strip() or DEFAULT_BLS_PREFIX

    s3_key = build_bls_s3_key(series_ids, bls_prefix)

    print(f"Bucket: {bucket_name}")
    print(f"Series IDs: {series_ids}")
    print(f"BLS S3 key: {s3_key}")

    data = fetch_bls_data(series_ids, api_key)
    upload_result = upload_if_changed(bucket_name, s3_key, data)

    print("Part 1 BLS ingest complete")

    return {
        "message": "Part 1 BLS ingest complete",
        "series_ids": series_ids,
        "bucket": bucket_name,
        "s3_key": s3_key,
        "upload": upload_result,
    }


def ingest_datausa(bucket_name: str) -> Dict[str, Any]:
    """
    Part 2: DataUSA ingest
    """
    print("Part 2 DataUSA ingest started")

    url = "https://honolulu-api.datausa.io/tesseract/data.jsonrecords?cube=acs_yg_total_population_1&drilldowns=Year%2CNation&locale=en&measures=Population"

    s3_key = "raw/datausa/datausa_population.json"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            response_body = response.read()
            response_json = json.loads(response_body)

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DataUSA API error {exc.code}: {error_body[:500]}") from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(f"DataUSA API request failed: {exc}") from exc

    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(response_json, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print("Part 2 DataUSA ingest complete")

    return {
        "message": "Part 2 DataUSA ingest complete",
        "bucket": bucket_name,
        "s3_key": s3_key,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Part 4: Combined scheduled ingestion Lambda

    Runs:
    1. Part 1 BLS ingest
    2. Part 2 DataUSA ingest
    """
    print("Part 4 combined ingest started")

    bucket_name = get_required_env("BUCKET_NAME")

    results = {}

    try:
        results["part1_bls"] = ingest_bls(bucket_name)

    except Exception as e:
        print("Part 1 BLS failed:", str(e))

        results["part1_bls"] = {
            "status": "failed",
            "error": str(e),
        }

    try:
        results["part2_datausa"] = ingest_datausa(bucket_name)

    except Exception as e:
        print("Part 2 DataUSA failed:", str(e))

        results["part2_datausa"] = {
            "status": "failed",
            "error": str(e),
        }

    print("Part 4 combined ingest complete")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Part 4 combined ingest complete",
                "results": results,
            }
        ),
    }
