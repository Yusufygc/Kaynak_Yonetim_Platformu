from pydantic_settings import BaseSettings

from core.paths import resource_path, user_data_dir

_USER_DIR = user_data_dir()
_DB_PATH = _USER_DIR / "pkm_app.db"
_LOG_PATH = _USER_DIR / "app.log"
_ENV_FILE = resource_path("..", ".env")


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = f"sqlite:///{_DB_PATH.as_posix()}"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = str(_LOG_PATH)
    DEFAULT_THEME: str = "dark"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
