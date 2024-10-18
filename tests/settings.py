import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.exceptions import ConfigFileNotFoundException, MandatoryEnvironmentVariableNotDefinedException


class Settings(BaseSettings):
    dummy_value: int = 0

    model_config = SettingsConfigDict(env_file_encoding="utf-8")


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
