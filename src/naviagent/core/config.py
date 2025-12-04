from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

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
