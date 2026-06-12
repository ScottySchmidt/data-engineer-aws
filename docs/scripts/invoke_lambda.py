# scripts/invoke_lambda.py
import json
import boto3

FUNCTION_NAME = "bls-github-ci-sandbox"  # your Lambda's name
REGION = "us-east-1"                     # match your Lambda's region

lam = boto3.client("lambda", region_name=REGION)
resp = lam.invoke(FunctionName=FUNCTION_NAME,
                  InvocationType="RequestResponse",
                  Payload=b'{}')

print("Status:", resp["StatusCode"])

raw = resp["Payload"].read().decode()
try:
    body = json.loads(raw)
    if isinstance(body, dict) and "body" in body:
        body = json.loads(body["body"])
    print("Body:", body)
except Exception:
    print("Body:", raw)
