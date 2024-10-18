import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.exceptions import ConfigFileNotFoundException, MandatoryEnvironmentVariableNotDefinedException


class Settings(BaseSettings):
    dummy_value: int = 0
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/todo_db"
    secret_key: str = "secret key"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "1111"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    mail_from_name: str = "ImageIQ"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def load_settings_from_file(settings_file: str) -> Settings:
    if not os.path.exists(settings_file):
        raise ConfigFileNotFoundException(
            f"The settings file {settings_file} could not be found."
        )
    return Settings(_env_file=settings_file)


def get_mandatory_environment_variable(environment_variable_name: str) -> str:
    """None is not considered a valid value."""
    value = os.getenv(environment_variable_name)
    if value is None:
        raise MandatoryEnvironmentVariableNotDefinedException(
            f"The {environment_variable_name} environment variable is mandatory."
        )
    return value


def load_settings_from_environment(environment_name: str, settings_dir: str = None) -> Settings:
    environment_value = get_mandatory_environment_variable(environment_name).strip().lower()
    config_file = os.path.join(settings_dir, f"{environment_value}.env")
    return load_settings_from_file(config_file)


settings = load_settings_from_file(settings_file=".env")