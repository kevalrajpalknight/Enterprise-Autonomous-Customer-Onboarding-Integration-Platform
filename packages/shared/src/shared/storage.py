from __future__ import annotations

import contextlib
from typing import Final

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# MIME type → file extension for storage key generation
DOCUMENT_MIME_TO_EXT: dict[str, str] = {
    "application/pdf": ".pdf",
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/json": ".json",
    "application/octet-stream": ".sql",
}

ALLOWED_MIME_TYPES: frozenset[str] = frozenset(DOCUMENT_MIME_TO_EXT)

# Default presigned URL TTLs
_UPLOAD_TTL: Final = 15 * 60  # 15 min — enough for a single upload attempt
_DOWNLOAD_TTL: Final = 60 * 60  # 1 hr


class StorageClient:
    """S3-compatible storage client. Tested against AWS S3 and Cloudflare R2."""

    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region: str = "auto",
    ) -> None:
        self._bucket = bucket_name
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
            # s3v4 required by Cloudflare R2 and most S3-compatible backends
            config=Config(signature_version="s3v4"),
        )

    # ── Key generation ───────────────────────────────────────────────────────

    @staticmethod
    def make_key(customer_id: str, document_id: str, mime_type: str) -> str:
        """Return a namespaced, deterministic storage key for a document."""
        ext = DOCUMENT_MIME_TO_EXT.get(mime_type, "")
        return f"documents/{customer_id}/{document_id}{ext}"

    # ── Server-side upload ───────────────────────────────────────────────────

    def upload_bytes(self, data: bytes, key: str, mime_type: str) -> None:
        """Upload raw bytes directly from the server (used in multipart form flow)."""
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=mime_type,
        )

    # ── Server-side download ─────────────────────────────────────────────────

    def download_bytes(self, key: str) -> bytes:
        """Download an object's raw bytes directly (used by worker-side processing)."""
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        body: bytes = response["Body"].read()
        return body

    # ── Presigned URLs ───────────────────────────────────────────────────────

    def presigned_upload_url(
        self,
        key: str,
        mime_type: str,
        expires_in: int = _UPLOAD_TTL,
    ) -> str:
        """Return a presigned PUT URL for direct client-to-S3 upload."""
        url: str = self._client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self._bucket, "Key": key, "ContentType": mime_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        return url

    def presigned_download_url(
        self,
        key: str,
        expires_in: int = _DOWNLOAD_TTL,
    ) -> str:
        """Return a presigned GET URL for secure, time-limited object access."""
        url: str = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    # ── Delete ───────────────────────────────────────────────────────────────

    def delete_object(self, key: str) -> None:
        """Delete an object by storage key. Silently ignores missing objects."""
        with contextlib.suppress(ClientError):
            self._client.delete_object(Bucket=self._bucket, Key=key)
