"""Application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the PharmaTrybe backend bootstrap."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="PharmaTrybe API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")
    soar_service_url: str = Field(default="", alias="SOAR_SERVICE_URL")
    armd_service_url: str = Field(default="", alias="ARMD_SERVICE_URL")
    who_service_url: str = Field(default="", alias="WHO_SERVICE_URL")
    decision_engine_url: str = Field(default="", alias="DECISION_ENGINE_URL")
    explainability_url: str = Field(default="", alias="EXPLAINABILITY_URL")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    debug: bool = Field(default=False, alias="DEBUG")


settings = Settings()
