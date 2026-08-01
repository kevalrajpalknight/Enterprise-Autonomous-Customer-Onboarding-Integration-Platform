from functools import cache

from shared.storage import StorageClient

from api.config import settings


@cache
def get_storage_client() -> StorageClient:
    return StorageClient(
        endpoint_url=settings.s3_endpoint_url,
        access_key_id=settings.s3_access_key_id,
        secret_access_key=settings.s3_secret_access_key,
        bucket_name=settings.s3_bucket_name,
        region=settings.s3_region,
    )
