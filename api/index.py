"""Vercel ASGI entrypoint; use the same API and owner-isolated demos as locally."""
import os
import sys
from pathlib import Path

# Fail closed: serverless filesystems are ephemeral, never a demo database.
if not os.environ.get("DATABASE_URL", "").startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
    raise RuntimeError("Vercel requires a persistent PostgreSQL DATABASE_URL")
os.environ["ENVIRONMENT"] = "production"
os.environ["COOKIE_SECURE"] = "true"
os.environ["AI_MODE"] = "unavailable"

# Alembic revisions and the local launcher share the canonical `app` package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.main import app  # noqa: E402,F401
