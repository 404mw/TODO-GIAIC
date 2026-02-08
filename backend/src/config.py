"""Application configuration using Pydantic Settings.

Loads configuration from environment variables and .env file.
All settings are validated at startup.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # DATABASE
    # ==========================================================================
    database_url: SecretStr = Field(
        ...,
        description="PostgreSQL connection string (asyncpg)",
    )

    # ==========================================================================
    # JWT CONFIGURATION
    # ==========================================================================
    # Keys can be provided inline OR via file paths (file paths take precedence)
    jwt_private_key: SecretStr = Field(
        default=SecretStr(""),
        description="RSA private key for signing JWTs (PEM format, inline)",
    )
    jwt_public_key: str = Field(
        default="",
        description="RSA public key for verifying JWTs (PEM format, inline)",
    )
    jwt_private_key_path: str | None = Field(
        default=None,
        description="Path to RSA private key file (overrides jwt_private_key)",
    )
    jwt_public_key_path: str | None = Field(
        default=None,
        description="Path to RSA public key file (overrides jwt_public_key)",
    )
    jwt_algorithm: str = Field(
        default="RS256",
        description="JWT signing algorithm",
    )
    jwt_access_expiry_minutes: int = Field(
        default=15,
        ge=1,
        le=60,
        description="Access token expiry in minutes",
    )
    jwt_refresh_expiry_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Refresh token expiry in days",
    )

    def get_jwt_private_key(self) -> str:
        """Get JWT private key from file or inline value."""
        if self.jwt_private_key_path:
            with open(self.jwt_private_key_path) as f:
                return f.read()
        return self.jwt_private_key.get_secret_value()

    def get_jwt_public_key(self) -> str:
        """Get JWT public key from file or inline value."""
        if self.jwt_public_key_path:
            with open(self.jwt_public_key_path) as f:
                return f.read()
        return self.jwt_public_key

    # ==========================================================================
    # GOOGLE OAUTH
    # ==========================================================================
    google_client_id: str = Field(
        ...,
        description="Google OAuth client ID",
    )
    google_client_secret: SecretStr = Field(
        ...,
        description="Google OAuth client secret",
    )

    # ==========================================================================
    # OPENAI (AI FEATURES)
    # ==========================================================================
    openai_api_key: SecretStr = Field(
        ...,
        description="OpenAI API key",
    )
    openai_model: str = Field(
        default="gpt-4-turbo",
        description="OpenAI model for AI features",
    )

    # ==========================================================================
    # DEEPGRAM (VOICE TRANSCRIPTION)
    # ==========================================================================
    deepgram_api_key: SecretStr = Field(
        ...,
        description="Deepgram API key for voice transcription",
    )
    deepgram_timeout_seconds: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Deepgram API timeout in seconds",
    )
    deepgram_model: str = Field(
        default="nova-2",
        description="Deepgram model for transcription (NOVA2)",
    )
    max_audio_duration_seconds: int = Field(
        default=300,
        ge=1,
        le=300,
        description="Maximum audio duration for transcription (FR-036)",
    )

    # ==========================================================================
    # WEBPUSH (PUSH NOTIFICATIONS - FR-028a)
    # ==========================================================================
    vapid_private_key: SecretStr = Field(
        default=SecretStr(""),
        description="VAPID private key for WebPush (base64)",
    )
    vapid_contact_email: str = Field(
        default="admin@perpetua.flow",
        description="VAPID contact email for WebPush",
    )

    # ==========================================================================
    # CHECKOUT.COM (PAYMENTS)
    # ==========================================================================
    checkout_secret_key: SecretStr = Field(
        default=SecretStr(""),
        description="Checkout.com secret key",
    )
    checkout_webhook_secret: SecretStr = Field(
        default=SecretStr(""),
        description="Checkout.com webhook secret",
    )

    # ==========================================================================
    # RATE LIMITS (FR-061)
    # ==========================================================================
    rate_limit_general: int = Field(
        default=100,
        ge=1,
        description="General API rate limit (requests per minute)",
    )
    rate_limit_ai: int = Field(
        default=20,
        ge=1,
        description="AI endpoints rate limit (requests per minute)",
    )
    rate_limit_auth: int = Field(
        default=10,
        ge=1,
        description="Auth endpoints rate limit (requests per minute per IP)",
    )

    # ==========================================================================
    # AI CREDITS CONFIGURATION
    # ==========================================================================
    ai_credit_chat: int = Field(
        default=1,
        ge=1,
        description="Credits per chat message",
    )
    ai_credit_subtask: int = Field(
        default=1,
        ge=1,
        description="Credits per subtask generation",
    )
    ai_credit_conversion: int = Field(
        default=1,
        ge=1,
        description="Credits per note-to-task conversion",
    )
    ai_credit_transcription_per_min: int = Field(
        default=5,
        ge=1,
        description="Credits per minute of voice transcription",
    )
    kickstart_credits: int = Field(
        default=5,
        ge=0,
        description="One-time kickstart credits for new users",
    )
    pro_daily_credits: int = Field(
        default=10,
        ge=0,
        description="Daily AI credits for Pro users",
    )
    pro_monthly_credits: int = Field(
        default=100,
        ge=0,
        description="Monthly AI credits for Pro users",
    )
    max_credit_carryover: int = Field(
        default=50,
        ge=0,
        description="Maximum subscription credits that carry over",
    )

    # ==========================================================================
    # TIER LIMITS
    # ==========================================================================
    free_max_tasks: int = Field(default=50, ge=1)
    pro_max_tasks: int = Field(default=200, ge=1)
    free_max_subtasks: int = Field(default=4, ge=1)
    pro_max_subtasks: int = Field(default=10, ge=1)
    free_max_notes: int = Field(default=10, ge=1)
    pro_max_notes: int = Field(default=25, ge=1)
    free_desc_max_length: int = Field(default=1000, ge=100)
    pro_desc_max_length: int = Field(default=2000, ge=100)

    # ==========================================================================
    # FEATURE FLAGS
    # ==========================================================================
    enable_voice_transcription: bool = Field(
        default=True,
        description="Enable voice transcription feature",
    )

    # ==========================================================================
    # APPLICATION SETTINGS
    # ==========================================================================
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=False,
        description="Debug mode (DO NOT enable in production)",
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="API base URL",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() if you need to reload settings.
    """
    return Settings()
