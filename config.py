import os
import socket
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


# Load .env before reading environment variables so local development gets the
# same config path as production without extra shell setup.
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
POSTGRES_SCHEMES = {"postgres", "postgresql", "postgresql+psycopg", "postgresql+psycopg2"}


@dataclass(frozen=True)
class DatabaseConfig:
    uri: str
    db_type: str
    hostname: str | None = None
    provider: str | None = None


def _normalize_postgres_uri(database_url: str) -> str:
    """Normalize Render/Supabase style Postgres URLs for SQLAlchemy + psycopg2."""
    database_url = database_url.strip()

    # Some platforms still expose postgres://, while SQLAlchemy expects the
    # postgresql dialect name.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Use the psycopg2 driver.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # Ensure sslmode=require query parameter is set for Supabase/PostgreSQL secure connection
    if "sslmode=" not in database_url:
        if "?" in database_url:
            database_url += "&sslmode=require"
        else:
            database_url += "?sslmode=require"

    return database_url


def _clean_database_url(database_url: str) -> str:
    return database_url.strip().strip('"').strip("'")


def _detect_provider(hostname: str | None) -> str | None:
    if not hostname:
        return None
    host = hostname.lower()
    if "supabase" in host:
        return "Supabase"
    if "render" in host:
        return "Render"
    return None


def _validate_database_url(database_url: str) -> DatabaseConfig:
    raw_url = _clean_database_url(database_url)
    if not raw_url:
        raise RuntimeError("CRITICAL: DATABASE_URL is empty!")

    try:
        parsed = make_url(raw_url)
    except ArgumentError as exc:
        raise RuntimeError(f"CRITICAL: DATABASE_URL is malformed: {exc}")

    if parsed.drivername not in POSTGRES_SCHEMES:
        raise RuntimeError(f"CRITICAL: DATABASE_URL uses unsupported scheme '{parsed.drivername}'!")

    if not parsed.host:
        raise RuntimeError("CRITICAL: DATABASE_URL does not include a hostname!")



    normalized_uri = _normalize_postgres_uri(raw_url)
    normalized = make_url(normalized_uri)
    return DatabaseConfig(
        uri=normalized_uri,
        db_type="postgresql",
        hostname=normalized.host,
        provider=_detect_provider(normalized.host),
    )


def get_database_uri() -> str:
    return get_database_config().uri


def get_database_config() -> DatabaseConfig:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url.strip():
        raise RuntimeError("CRITICAL: DATABASE_URL environment variable is missing!")

    return _validate_database_url(database_url)


class Config:
    DB_CONFIG = get_database_config()
    DATABASE_URL_DETECTED = True
    SQLALCHEMY_DATABASE_URI = DB_CONFIG.uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
