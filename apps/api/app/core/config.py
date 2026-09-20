"""Central application configuration using Pydantic Settings."""

from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

API_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_PATH = Path(__file__).resolve()
PROJECT_ROOT = (
    _CONFIG_PATH.parents[4]
    if len(_CONFIG_PATH.parents) > 4
    else API_PROJECT_ROOT
)


class Settings(BaseSettings):
    """Runtime configuration for the PharmaTrybe backend bootstrap."""

    model_config = SettingsConfigDict(
        env_file=[PROJECT_ROOT / ".env", API_PROJECT_ROOT / ".env"],
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(default="PharmaTrybe API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    database_url: str = Field(default="", alias="DATABASE_URL")
    who_database_url: str = Field(default="", alias="WHO_DATABASE_URL")
    invitation_handoff_encryption_key: str = Field(default="", alias="INVITATION_HANDOFF_ENCRYPTION_KEY")
    invitation_frontend_route: str = Field(default="", alias="INVITATION_FRONTEND_ROUTE")

    # API runtime
    api_prefix: str = Field(default="", alias="API_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Timeout and retry defaults
    default_timeout_seconds: float = Field(default=5.0, alias="DEFAULT_TIMEOUT_SECONDS")
    default_retry_count: int = Field(default=0, alias="DEFAULT_RETRY_COUNT")
    default_retry_backoff_seconds: float = Field(default=0.0, alias="DEFAULT_RETRY_BACKOFF_SECONDS")

    # Supabase integration contract. Values are supplied by the deployment
    # environment; no production credential or signing value belongs here.
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_issuer: str = Field(default="", alias="SUPABASE_JWT_ISSUER")
    supabase_jwt_audience: str = Field(default="", alias="SUPABASE_JWT_AUDIENCE")
    supabase_jwks_url: str = Field(default="", alias="SUPABASE_JWKS_URL")
    supabase_jwt_algorithms: str = Field(default="ES256,RS256", alias="SUPABASE_JWT_ALGORITHMS")

    # Service endpoints (placeholders only)
    soar_service_url: str = Field(default="", alias="SOAR_SERVICE_URL")
    armd_service_url: str = Field(default="", alias="ARMD_SERVICE_URL")
    who_service_url: str = Field(default="", alias="WHO_SERVICE_URL")
    decision_engine_url: str = Field(default="", alias="DECISION_ENGINE_URL")
    explainability_url: str = Field(default="", alias="EXPLAINABILITY_URL")

    # Feature flags
    enable_cors: bool = Field(default=True, alias="ENABLE_CORS")
    enable_trusted_host_middleware: bool = Field(default=True, alias="ENABLE_TRUSTED_HOST_MIDDLEWARE")
    enable_request_logging: bool = Field(default=True, alias="ENABLE_REQUEST_LOGGING")
    enable_security_headers: bool = Field(default=True, alias="ENABLE_SECURITY_HEADERS")

    @model_validator(mode="after")
    def validate_invitation_delivery_configuration(self) -> "Settings":
        """Require secure invitation delivery settings outside local development."""
        if self.invitation_handoff_encryption_key:
            try:
                Fernet(self.invitation_handoff_encryption_key.encode())
            except (ValueError, InvalidToken) as exc:
                raise ValueError("INVITATION_HANDOFF_ENCRYPTION_KEY must be a valid Fernet key") from exc
        if self.environment.lower() in {"production", "staging"}:
            if not self.invitation_handoff_encryption_key:
                raise ValueError("INVITATION_HANDOFF_ENCRYPTION_KEY is required outside development")
            if not self.invitation_frontend_route:
                raise ValueError("INVITATION_FRONTEND_ROUTE is required outside development")
        return self


settings = Settings()
