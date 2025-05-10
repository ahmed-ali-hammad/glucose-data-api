from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration class.

    This class uses Pydantic's `BaseSettings` to manage and validate
    environment variables.
    """

    LOG_LEVEL: str = "DEBUG"

    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_URI: str | None = None  # Really only used by Alembic for migrations
    ASYNC_DATABASE_URI: str | None = None

    @field_validator("DATABASE_URI", mode="before")
    def build_database_uri(cls, v, info: ValidationInfo):
        values = info.data
        try:
            return f"mysql://{values['DATABASE_USER']}:{values['DATABASE_PASSWORD']}@{values['DATABASE_HOST']}:{values['DATABASE_PORT']}/{values['DATABASE_NAME']}?charset=utf8mb4"
        except KeyError as e:
            raise ValueError(f"Missing database configuration value: {e}")

    @field_validator("ASYNC_DATABASE_URI", mode="before")
    def build_async_database_uri(cls, v, info: ValidationInfo):
        values = info.data
        try:
            return f"mysql+asyncmy://{values['DATABASE_USER']}:{values['DATABASE_PASSWORD']}@{values['DATABASE_HOST']}:{values['DATABASE_PORT']}/{values['DATABASE_NAME']}?charset=utf8mb4"
        except KeyError as e:
            raise ValueError(f"Missing database configuration value: {e}")
