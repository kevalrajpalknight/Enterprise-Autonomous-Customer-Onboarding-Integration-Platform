from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Rate limiting
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60

    # Storage
    max_upload_bytes: int = 50 * 1024 * 1024  # 50 MB

    # Database
    database_url: str = "postgresql+asyncpg://onboardai:onboardai@localhost:5432/onboardai"

    # S3-compatible object storage (AWS S3 or Cloudflare R2)
    s3_endpoint_url: str = "https://s3.amazonaws.com"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = "onboardai-documents"
    s3_region: str = "us-east-1"


settings = Settings()
