from __future__ import annotations

"""Entrypoint to run the FastAPI app with Uvicorn.

Use: python run.py
"""

import os

import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run("src.naviagent.main:app", host=host, port=port, reload=True)
