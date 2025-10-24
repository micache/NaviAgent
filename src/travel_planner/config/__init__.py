"""
Configuration settings for Travel Planner API
"""
import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "Travel Planner API"
    app_version: str = "1.0.0"
    api_prefix: str = "/v1"
    
    # OpenAI Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False  # Tắt reload mode
    
    # CORS Settings
    allow_origins: Union[str, List[str]] = "*"
    allow_credentials: bool = True
    allow_methods: Union[str, List[str]] = "*"
    allow_headers: Union[str, List[str]] = "*"
    
    @field_validator('allow_origins', 'allow_methods', 'allow_headers', mode='before')
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(',')]
        return v
    
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


# Create global settings instance
settings = Settings()

# Debug: Print loaded values
def debug_print_settings():
    print(f"[Config] API Key loaded: {'Yes' if settings.openai_api_key else 'No'}")
    if settings.openai_api_key:
        print(f"[Config] API Key starts with: {settings.openai_api_key[:10]}...")

# Only run debug prints if this module is the entry point
if __name__ == "__main__":
    debug_print_settings()
