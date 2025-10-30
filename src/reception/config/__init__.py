import os
from pathlib import Path
from typing import List, Union
import certifi
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
print(f"Loading from: {env_path}")

load_dotenv(dotenv_path=env_path, override=True)

class Settings(BaseSettings):
    # API Settings
    app_name: str = "NaviAgent Reception API"
    app_version: str = "1.0.0"
    api_prefix: str = "/receptionist_v1"
    
    # CORS Settings
    allow_origins: Union[List[str], str] = "*"
    allow_credentials: bool = True
    allow_methods: Union[List[str], str] = "*"
    allow_headers: Union[List[str], str] = "*"
    
    # OpenAI Settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL")
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    @field_validator("allow_origins", "allow_methods", "allow_headers", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
settings = Settings()

# Debug: Print loaded values
def debug_print_settings():
    print(f"[Config] API Key loaded: {'Yes' if settings.openai_api_key else 'No'}")
    if settings.openai_api_key:
        print(f"[Config] API Key starts with: {settings.openai_api_key[:10]}...")


# Only run debug prints if this module is the entry point
if __name__ == "__main__":
    debug_print_settings()