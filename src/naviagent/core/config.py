"""Application configuration helpers.

This module loads environment variables required to connect to Supabase.
We keep the configuration small and explicit so the rest of the codebase
can import from here without re-reading environment or duplicating logic.

Environment variables:
- SUPABASE_URL:     The Supabase project URL
- SUPABASE_ANON_KEY:The Supabase anon/public API key (NOT service role)
- SUPABASE_SERVICE_ROLE_KEY: The Supabase service role key (server-side only)

Notes:
- We skip hard failures if variables are missing at import time so that
  unit tests which don't require Supabase can still import. Runtime code
  that needs Supabase will validate and raise appropriate HTTP errors.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


# Try to load .env if python-dotenv is available. It's optional.
from dotenv import load_dotenv  # type: ignore
load_dotenv()


@dataclass(frozen=True)
class Settings:
    supabase_url: Optional[str]
    supabase_anon_key: Optional[str]
    supabase_service_role_key: Optional[str]


def get_settings() -> Settings:
    """Return current Settings from environment."""
    
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    )


settings = get_settings()
