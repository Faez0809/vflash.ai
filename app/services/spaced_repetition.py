from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models import UserWord, Word


def schedule_word_for_review(user_word, today=None):
    """Schedule the first three review checkpoints for a newly learned word."""
    today = today or date.today()
    user_word.learned = True
    user_word.learned_at = user_word.learned_at or today
    user_word.rev1 = today + timedelta(days=1)
    user_word.rev2 = today + timedelta(days=3)
    user_word.rev3 = today + timedelta(days=7)
    user_word.last_reviewed = today


def clear_due_reviews(user_word, today=None):
    """Mark any due review checkpoints as completed."""
    today = today or date.today()
    user_word.last_reviewed = today
    if user_word.rev1 and user_word.rev1 <= today:
        user_word.rev1 = None
    if user_word.rev2 and user_word.rev2 <= today:
        user_word.rev2 = None
    if user_word.rev3 and user_word.rev3 <= today:
        user_word.rev3 = None


def get_due_review_words(user_id):
    """Return learned words whose next review date is due today or overdue."""
    today = date.today()
    return (
        UserWord.query.options(selectinload(UserWord.word_entry))
        .filter_by(user_id=user_id, learned=True, already_known=False)
        .join(Word)
        .filter(Word.is_valid.is_(True))
        .filter(
            (UserWord.rev1.isnot(None) & (UserWord.rev1 <= today))
            | (UserWord.rev2.isnot(None) & (UserWord.rev2 <= today))
            | (UserWord.rev3.isnot(None) & (UserWord.rev3 <= today))
        )
        .order_by(UserWord.last_reviewed.asc().nullsfirst(), Word.word.asc())
        .all()
    )


def get_due_review_word_count(user_id):
    """Count due reviews without loading every row into memory."""
    today = date.today()
    return (
        UserWord.query.with_entities(func.count(UserWord.id))
        .filter_by(user_id=user_id, learned=True, already_known=False)
        .join(Word)
        .filter(Word.is_valid.is_(True))
        .filter(
            (UserWord.rev1.isnot(None) & (UserWord.rev1 <= today))
            | (UserWord.rev2.isnot(None) & (UserWord.rev2 <= today))
            | (UserWord.rev3.isnot(None) & (UserWord.rev3 <= today))
        )
        .scalar()
        or 0
    )
