"""
S3 (or any S3-compatible provider — R2, MinIO, etc.) storage backend.

NOTE: this code path is not exercised by the test suite in this project
because no AWS credentials are available in the build environment. It
follows the standard boto3 patterns, but verify it against your own
bucket/IAM policy before trusting it in production.
"""
import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.storage.base import StorageBackend


class S3Storage(StorageBackend):
    def __init__(self):
        client_kwargs = {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "region_name": settings.AWS_REGION,
        }
        if settings.AWS_S3_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL

        self.client = boto3.client("s3", **client_kwargs)
        self.bucket = settings.AWS_S3_BUCKET
        if not self.bucket:
            raise RuntimeError("AWS_S3_BUCKET must be set when STORAGE_BACKEND=s3")

    def save(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return key

    def read(self, key: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
            return obj["Body"].read()
        except ClientError as e:
            raise FileNotFoundError(f"S3 object not found: {key}") from e

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def url_for(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
