from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from naviagent.routers import auth as auth_router
from naviagent.routers import chat as chat_router
from naviagent.routers import trips as trips_router
from naviagent.routers import users as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="NaviAgent API", version="0.1.0")

    # CORS middleware - allow frontend to access API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js dev server
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

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
