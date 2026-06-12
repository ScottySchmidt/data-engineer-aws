import os, uuid, boto3, pytest

def test_env_present():
    for var in ("AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_REGION","BUCKET_NAME","BLS_API_KEY"):
        assert os.getenv(var), f"Missing env var: {var}"

@pytest.mark.skipif(os.getenv("RUN_AWS_SMOKE") != "1", reason="AWS smoke off")
def test_s3_round_trip():
    bucket = os.environ["BUCKET_NAME"]
    region = os.getenv("AWS_REGION", "us-east-1")
    s3 = boto3.client("s3", region_name=region)

    key = f"ci-cd-test/smoketest-{uuid.uuid4().hex[:8]}.json"
    body = b'{"ping": true}'

    s3.put_object(Bucket=bucket, Key=key, Body=body)
    assert s3.head_object(Bucket=bucket, Key=key)["ResponseMetadata"]["HTTPStatusCode"] == 200
    got = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    assert got == body
    s3.delete_object(Bucket=bucket, Key=key)

