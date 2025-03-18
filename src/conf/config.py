import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.exceptions import (ConfigFileNotFoundException,
                              MandatoryEnvironmentVariableNotDefinedException)


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/todo_db"
    secret_key: str = "secret key"
    algorithm: str = "HS256"
    mail_username: str = "example@ex.ua"
    mail_password: str = "1111"
    mail_from: str = "example@ex.ua"
    mail_from_name: str = "PostsAIcomments"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    google_sa_type: str = "google_sa_type"
    google_sa_project_id: str = "google_sa_project_id"
    google_sa_private_key_id: str = "google_sa_private_key_id"
    google_sa_private_key: str = "-----BEGIN PRIVATE KEY-----"
    google_sa_client_email: str = "google_sa_client_email"
    google_sa_client_id: str = "google_sa_client_id"
    google_sa_auth_uri: str = "https://"
    google_sa_token_uri: str = "https://"
    google_sa_auth_provider_x509_cert_url: str = "https://www.googleapis.com"
    google_sa_client_x509_cert_url: str = "https://www.googleapis.com"
    google_sa_universe_domain: str = "google_sa_universe_domain"
    google_sa_location: str = "GOOGLE_SA_LOCATION"

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")


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


settings = Settings()
