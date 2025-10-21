from __future__ import annotations

from fastapi import FastAPI

from .routers import auth as auth_router
from .routers import chat as chat_router
from .routers import trips as trips_router
from .routers import users as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="NaviAgent API", version="0.1.0")

    # Routers
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(chat_router.router)
    app.include_router(trips_router.router)

    @app.get("/health")
    def health():  # noqa: D401 - trivial
        """Simple health check endpoint."""
        return {"status": "ok"}

    return app


app = create_app()
