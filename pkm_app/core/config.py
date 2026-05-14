from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'pkm_app.db'}"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = str(BASE_DIR / "app.log")
    DEFAULT_THEME: str = "dark"

    class Config:
        env_file = BASE_DIR.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
