"""
Configuration settings for Travel Planner API
"""

import os
from pathlib import Path
from typing import List, Union

import certifi
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import model configuration
from .model_config import (
    AgentModelSettings,
    ModelConfig,
    ModelProvider,
    create_deepseek_config,
    create_default_config,
    create_gemini_config,
    create_hybrid_config,
    model_settings,
)


# Locate root-level .env (outside travel_planner) with fallback to local .env
def _find_env_file() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[3] / ".env",  # repository root
        Path(__file__).resolve().parents[2] / ".env",  # src/.env (fallback)
        Path(__file__).parent.parent / ".env",  # travel_planner/.env (last resort)
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


env_path = _find_env_file()
if env_path:
    load_dotenv(env_path, override=True)
    print(f"[Config] Loaded environment from {env_path}")
else:
    print("[Config] No .env file found; relying on existing environment")

# Ensure SSL/TLS uses the bundled certifi CA bundle on all platforms
_certifi_ca_bundle = certifi.where()
if _certifi_ca_bundle and os.path.exists(_certifi_ca_bundle):
    os.environ.setdefault("SSL_CERT_FILE", _certifi_ca_bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", _certifi_ca_bundle)
    # Helpful debug log so we can verify the cert bundle in runtime logs
    print(f"[Config] SSL cert bundle: {_certifi_ca_bundle}")


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Travel Planner API"
    app_version: str = "1.0.0"
    api_prefix: str = "/v1"

    # OpenAI Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8003
    reload: bool = False  # Tắt reload mode

    # CORS Settings
    allow_origins: Union[str, List[str]] = "*"
    allow_credentials: bool = True
    allow_methods: Union[str, List[str]] = "*"
    allow_headers: Union[str, List[str]] = "*"

    @field_validator("allow_origins", "allow_methods", "allow_headers", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=str(env_path) if env_path else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Create global settings instance
settings = Settings()


# Debug: Print loaded values
def debug_print_settings():
    print(f"[Config] API Key loaded: {'Yes' if settings.openai_api_key else 'No'}")
    if settings.openai_api_key:
        print(f"[Config] API Key starts with: {settings.openai_api_key[:10]}...")


# Export all configuration components
__all__ = [
    "settings",
    "Settings",
    "model_settings",
    "ModelProvider",
    "ModelConfig",
    "AgentModelSettings",
    "create_default_config",
    "create_gemini_config",
    "create_deepseek_config",
    "create_hybrid_config",
]

# Only run debug prints if this module is the entry point
if __name__ == "__main__":
    debug_print_settings()
