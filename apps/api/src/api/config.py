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


settings = Settings()
