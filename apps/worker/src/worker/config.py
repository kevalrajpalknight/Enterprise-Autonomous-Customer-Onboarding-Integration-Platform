from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Redis / Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Database
    database_url: str = "postgresql+asyncpg://onboardai:onboardai@localhost:5432/onboardai"

    # S3-compatible object storage (AWS S3 or Cloudflare R2)
    s3_endpoint_url: str = "https://s3.amazonaws.com"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = "onboardai-documents"
    s3_region: str = "us-east-1"

    # Vision LLM
    vision_llm_provider: str = "openai"
    vision_llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    vision_page_dpi: int = 200


settings = Settings()
