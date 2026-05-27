import time
from collections import OrderedDict

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.models import (
    FlashcardSession,
    FlashcardSessionWord,
    SearchHistory,
    User,
    UserLevelProgress,
    UserWordProgress,
    VocabularyEnrichment,
    VocabularyMaster,
    VocabularyReviewFlag,
    db,
)


REQUIRED_TABLES = (
    "vocabulary_master",
    "vocabulary_enrichment",
    "user_word_progress",
    "user_level_progress",
    "flashcard_sessions",
    "flashcard_session_words",
    "search_history",
    "vocabulary_review_flags",
)

COUNT_MODELS = OrderedDict(
    (
        ("vocabulary_master", VocabularyMaster),
        ("users", User),
        ("vocabulary_enrichment", VocabularyEnrichment),
        ("user_word_progress", UserWordProgress),
        ("user_level_progress", UserLevelProgress),
        ("flashcard_sessions", FlashcardSession),
        ("flashcard_session_words", FlashcardSessionWord),
        ("search_history", SearchHistory),
        ("vocabulary_review_flags", VocabularyReviewFlag),
    )
)


def default_database_health(error=None):
    return {
        "database_url_detected": True,
        "db_type": "postgresql",
        "database_type": "postgresql",
        "provider": "Supabase",
        "host": "unknown",
        "database": "unknown",
        "database_name": "unknown",
        "status": "error" if error else "unknown",
        "healthy": False,
        "connection_error": str(error) if error else None,
        "error": str(error) if error else None,
        "missing_tables": [],
        "counts": {},
        "level_counts": {},
        "alembic_version": "unknown",
        "migration_version": "unknown",
        "vocabulary_count": 0,
        "user_count": 0,
        "enrichment_count": 0,
        "total_progress_rows": 0,
        "latency_ms": 0.0,
    }


def _safe_rollback():
    try:
        db.session.rollback()
    except Exception:
        pass


def get_database_health(app):
    health = default_database_health()

    try:
        db_config = app.config.get("DB_CONFIG")
        health.update(
            {
                "database_url_detected": True,
                "db_type": "postgresql",
                "database_type": "postgresql",
                "provider": getattr(db_config, "provider", "Supabase") if db_config else "Supabase",
                "host": getattr(db_config, "hostname", "unknown") if db_config else "unknown",
                "database": None,
                "database_name": "unknown",
                "status": "ok",
                "healthy": True,
                "connection_error": None,
                "error": None,
                "missing_tables": [],
                "counts": {},
                "level_counts": {},
                "alembic_version": None,
                "migration_version": "unknown",
                "total_progress_rows": 0,
                "latency_ms": 0.0,
            }
        )
        engine_url = db.engine.url
        health["database"] = engine_url.database
        health["database_name"] = engine_url.database or "unknown"
        health["host"] = health["host"] or engine_url.host

        # Measure DB latency
        start_time = time.time()
        db.session.execute(text("SELECT 1"))
        health["latency_ms"] = round((time.time() - start_time) * 1000, 2)

        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())
        health["missing_tables"] = [table for table in REQUIRED_TABLES if table not in tables]
        if health["missing_tables"]:
            health["status"] = "schema_missing"
            health["healthy"] = False

        if "alembic_version" in tables:
            health["alembic_version"] = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
            health["migration_version"] = health["alembic_version"] or "unknown"

        for label, model in COUNT_MODELS.items():
            table_name = model.__tablename__
            health["counts"][label] = model.query.count() if table_name in tables else None
        health["vocabulary_count"] = int(health["counts"].get("vocabulary_master") or 0)
        health["user_count"] = int(health["counts"].get("users") or 0)
        health["enrichment_count"] = int(health["counts"].get("vocabulary_enrichment") or 0)
        health["total_progress_rows"] = int(health["counts"].get("user_word_progress") or 0)

        if "vocabulary_master" in tables:
            health["level_counts"] = {
                level: count
                for level, count in db.session.query(VocabularyMaster.level, db.func.count(VocabularyMaster.id))
                .group_by(VocabularyMaster.level)
                .all()
            }
    except SQLAlchemyError as exc:
        _safe_rollback()
        health["status"] = "error"
        health["healthy"] = False
        health["connection_error"] = str(exc)
        health["error"] = str(exc)
    except Exception as exc:
        _safe_rollback()
        health = default_database_health(exc)

    return health


def print_database_health(app):
    health = get_database_health(app)
    print(f"[DB] Connected DB type: {health['db_type']}")
    print(f"[DB] Host: {health['host']}")
    print(f"[DB] Database name: {health['database']}")
    print(f"[DB] Health status: {health['status']}")
    print(f"[DB] Latency (Ping): {health['latency_ms']} ms")
    if health["missing_tables"]:
        print(f"[DB] Missing tables: {', '.join(health['missing_tables'])}")
    if health["connection_error"]:
        print(f"[DB] Connection error: {health['connection_error']}")
    print(f"[DB] vocabulary_master: {health['counts'].get('vocabulary_master')} rows")
    print(f"[DB] users: {health['counts'].get('users')} rows")
    print(f"[DB] vocabulary_enrichment: {health['counts'].get('vocabulary_enrichment')} rows")
    for level in ("intermediate", "upper_intermediate", "advanced"):
        print(f"[DB] vocabulary_master.{level}: {health['level_counts'].get(level, 0)} rows")
    if health["alembic_version"]:
        print(f"[DB] Alembic version: {health['alembic_version']}")
    return health
