from pathlib import Path
import sys

from sqlalchemy import inspect, text


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models import FlashcardSession, FlashcardSessionWord, LegacySavedNote, UserLevelProgress, UserWordProgress, db


LEGACY_TABLES_TO_CLEAR = (
    "user_word",
    "study_session",
)


def table_exists(table_name):
    return table_name in inspect(db.engine).get_table_names()


def reset_learning_journey(user_id=None):
    """Reset generated learning state while preserving accounts and searches."""
    filters = {}
    if user_id is not None:
        filters["user_id"] = int(user_id)

    try:
        if table_exists("user_word") and table_exists("word"):
            where_clause = "WHERE uw.note IS NOT NULL AND trim(uw.note) <> ''"
            params = {}
            if user_id is not None:
                where_clause += " AND uw.user_id = :user_id"
                params["user_id"] = int(user_id)
            note_rows = db.session.execute(
                text(
                    f"""
                    SELECT uw.user_id, w.word, uw.note
                    FROM user_word uw
                    JOIN word w ON w.id = uw.word_id
                    {where_clause}
                    """
                ),
                params,
            ).all()
            for note_user_id, word, note in note_rows:
                db.session.add(
                    LegacySavedNote(
                        user_id=note_user_id,
                        word=str(word or "").strip()[:180] or "unknown",
                        note=str(note or "").strip(),
                    )
                )

        session_ids = [
            row[0]
            for row in db.session.query(FlashcardSession.id).filter_by(**filters).all()
        ]
        if session_ids:
            FlashcardSessionWord.query.filter(FlashcardSessionWord.session_id.in_(session_ids)).delete(
                synchronize_session=False
            )
        FlashcardSession.query.filter_by(**filters).delete(synchronize_session=False)
        UserWordProgress.query.filter_by(**filters).delete(synchronize_session=False)
        UserLevelProgress.query.filter_by(**filters).delete(synchronize_session=False)

        if user_id is None:
            for table_name in LEGACY_TABLES_TO_CLEAR:
                if table_exists(table_name):
                    db.session.execute(text(f"DELETE FROM {table_name}"))
        else:
            if table_exists("user_word"):
                db.session.execute(text("DELETE FROM user_word WHERE user_id = :user_id"), {"user_id": int(user_id)})
            if table_exists("study_session"):
                db.session.execute(text("DELETE FROM study_session WHERE user_id = :user_id"), {"user_id": int(user_id)})
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return {
        "scope": "all_users" if user_id is None else f"user:{user_id}",
        "legacy_tables_cleared": list(LEGACY_TABLES_TO_CLEAR) if user_id is None else [],
    }


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        target_user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
        result = reset_learning_journey(target_user_id)
        print("Learning journey reset complete")
        print(f"Scope: {result['scope']}")
        if result["legacy_tables_cleared"]:
            print("Cleared legacy tables: " + ", ".join(result["legacy_tables_cleared"]))
