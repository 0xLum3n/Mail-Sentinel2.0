"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    app_name: str = Field(default="Mail Sentinel API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")

    secret_key: str = Field(validation_alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        gt=0,
    )
    refresh_token_expire_days: int = Field(
        default=14,
        validation_alias="REFRESH_TOKEN_EXPIRE_DAYS",
        gt=0,
    )

    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="mail_sentinel", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")

    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_password: str | None = Field(default=None, validation_alias="REDIS_PASSWORD")

    cors_origins: str = Field(
        default="http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    ai_provider: str | None = Field(default=None, validation_alias="AI_PROVIDER")
    ai_model: str | None = Field(default=None, validation_alias="AI_MODEL")
    ai_api_key: str | None = Field(default=None, validation_alias="AI_API_KEY")
    ai_base_url: str = Field(default="https://api.openai.com/v1", validation_alias="AI_BASE_URL")
    ai_timeout_seconds: float = Field(default=30.0, validation_alias="AI_TIMEOUT_SECONDS", gt=0)

    virustotal_api_key: str | None = Field(default=None, validation_alias="VIRUSTOTAL_API_KEY")
    abuseipdb_api_key: str | None = Field(default=None, validation_alias="ABUSEIPDB_API_KEY")
    urlscan_api_key: str | None = Field(default=None, validation_alias="URLSCAN_API_KEY")
    threat_intel_timeout_seconds: float = Field(
        default=8.0,
        validation_alias="THREAT_INTEL_TIMEOUT_SECONDS",
        gt=0,
    )
    threat_intel_cache_ttl_seconds: int = Field(
        default=3600,
        validation_alias="THREAT_INTEL_CACHE_TTL_SECONDS",
        gt=0,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Return the async SQLAlchemy PostgreSQL connection URL."""
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Return the Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a normalized list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
