import os

import boto3

S3_BUCKET = os.environ.get("S3_BUCKET")

_client = boto3.client(
    "s3",
    region_name=os.environ.get("AWS_REGION") or None,
)


def upload_document(local_path: str, key: str) -> str:
    _client.upload_file(local_path, S3_BUCKET, key)
    region = os.environ.get("AWS_REGION") or None
    if region:
        return f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{key}"
    return f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"
