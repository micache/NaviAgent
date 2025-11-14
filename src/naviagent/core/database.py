"""Supabase client initialization and helpers.

We create a single client per-process. For request-scoped behavior or
mocking in tests, you can override the dependency that uses this client.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException, status

try:
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover - supabase optional in CI
    create_client = None  # type: ignore
    Client = object  # type: ignore

from .config import settings

_client: Optional[Any] = None


def get_supabase() -> Any:
    """Get a configured Supabase client or raise an HTTP 500 if missing.

    We avoid raising at import time so that modules can be imported in
    environments where Supabase env vars are not present (e.g., tests).
    """

    global _client
    if _client is not None:
        return _client

    if create_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="supabase-py is not installed. Please add 'supabase' to requirements.",
        )

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment.",
        )

    _client = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _client


def get_supabase_authed(access_token: str) -> Any:
    """Create a new Supabase client for this request and attach a user token.

    This avoids sharing Authorization headers between concurrent requests and
    ensures Row Level Security policies evaluate with the correct auth context.
    """

    if create_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="supabase-py is not installed. Please add 'supabase' to requirements.",
        )

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment.",
        )

    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    # Attach Authorization header for PostgREST calls (RLS)
    if hasattr(client, "postgrest") and access_token:
        client.postgrest.auth(access_token)
    return client


def get_supabase_service() -> Any:
    """Return a Supabase client initialized with the service-role key.

    WARNING: The service-role key bypasses RLS. Never expose it to clients
    or use it in places where it could be leaked. Server-side only.
    """

    if create_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="supabase-py is not installed. Please add 'supabase' to requirements.",
        )

    service_key = settings.supabase_service_role_key
    if not settings.supabase_url or not service_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment. "
                "Either provide a service key or ensure a user access token is available."
            ),
        )

    client = create_client(settings.supabase_url, service_key)
    return client
