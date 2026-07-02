from pydantic import model_validator
from pydantic_settings import BaseSettings

from core.paths import resource_path, user_data_dir

_USER_DIR = user_data_dir()
_DB_PATH = _USER_DIR / "pkm_app.db"
_LOG_PATH = _USER_DIR / "app.log"
_ENV_FILE = resource_path("..", ".env")


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = f"sqlite:///{_DB_PATH.as_posix()}"
    LOG_LEVEL: str = ""
    LOG_FILE: str = str(_LOG_PATH)
    DEFAULT_THEME: str = "light"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"

    @model_validator(mode="after")
    def _default_log_level(self) -> "Settings":
        """LOG_LEVEL .env/ortam degiskeninde belirtilmemisse APP_ENV'e gore sec.

        .env dosyasiz (ornegin frozen exe) calisan bir prod kurulumunun
        yanlislikla DEBUG seviyesinde loglamamasi icin.
        """
        if not self.LOG_LEVEL:
            self.LOG_LEVEL = "DEBUG" if self.APP_ENV == "development" else "INFO"
        return self


settings = Settings()
