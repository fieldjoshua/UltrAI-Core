"""Phase 2 app - includes database health check"""

import os
from typing import Optional

from fastapi import FastAPI
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text


class Settings(BaseSettings):
    database_url: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env


settings = Settings()
app = FastAPI()


@app.get("/")
def root():
    return {"status": "alive", "phase": 2}


@app.get("/health")
def health():
    return {"status": "ok", "services": ["api"]}


@app.get("/health/database")
def health_database():
    """Check database connectivity"""
    if not settings.database_url:
        return {
            "status": "warning",
            "message": "No database URL configured",
            "database": "not_configured",
        }

    try:
        # Create engine and test connection
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "connection_failed", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))  # nosec # noqa
