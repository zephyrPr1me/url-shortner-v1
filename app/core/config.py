import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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

    DOMAIN_ZONES_FILE: str = str(BASE_DIR / "domain_zones.txt")
    ALLOWED_DOMAINS: list[str] = []

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if os.path.exists(self.DOMAIN_ZONES_FILE):
            domains = []
            with open(self.DOMAIN_ZONES_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    if line.strip():
                        domains.extend(
                            [d.strip() for d in line.split(",") if d.strip()]
                        )
            self.ALLOWED_DOMAINS = domains


settings = Settings()
