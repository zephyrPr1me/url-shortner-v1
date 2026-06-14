from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mysecretpassword123"
    POSTGRES_DB: str = "mydatabase"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # Base URL of this service, used for self-shortening protection.
    # Override via BASE_URL env variable in production.
    BASE_URL: str = "http://localhost:8000"

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self


settings = Settings()
