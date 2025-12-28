from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Notepad")
    notes_path: str = "/app/data/notes"
    allow_origin_regex: str = os.getenv("ALLOW_ORIGIN_REGEX", "")
    file_list_password: str = os.getenv("FILE_LIST_PASSWORD", "admin123")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "default-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    max_file_size: int = 100000
    max_filename_length: int = 200


settings = Settings()


def get_settings() -> Settings:
    return settings


def ensure_data_directory():
    os.makedirs(settings.notes_path, exist_ok=True)


ensure_data_directory()
