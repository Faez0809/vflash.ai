import os, sys
import pytest

# Force the application to use an in‑memory SQLite database for the test run.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Signal to the configuration loader that we are in a test environment.
os.environ["TESTING"] = "1"

# Ensure the project root is on the import path so that "app" can be resolved when tests run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ``create_app`` is imported inside the ``app`` fixture after the ``DATABASE_URL``
# environment variable is overridden to ensure SQLite is used.
from app.services.vocabulary_platform import create_flashcard_session, get_replacement_vocabulary
from app.models import db, User, VocabularyMaster, UserWordProgress, FlashcardSession
import app.models as models  # Ensure all model classes are imported for db.create_all()

@pytest.fixture
def app():
    """Create a Flask app for testing with an in‑memory SQLite database.
    The production configuration may point to PostgreSQL, which requires the
    ``psycopg2`` driver that is not installed in the test environment.  By
    temporarily setting ``DATABASE_URL`` to an SQLite memory URL before the
    application is created we force the ``Config`` loader to use SQLite and
    avoid the missing driver error.
    """
    import os
    from app import create_app  # Imported here after env var is set
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def user_id(app):
    """Create a test user and return its primary key.
    Returning the raw ``id`` avoids ``DetachedInstanceError`` when the user
    instance is accessed outside the original session.
    """
    with app.app_context():
        u = User(email="test@example.com", password="hash")
        db.session.add(u)
        db.session.commit()
        return u.id

def populate_vocab(level, count, needs_admin_review=False):
    vocab_list = []
    for i in range(count):
        v = VocabularyMaster(word=f"word{i}", normalized_word=f"word{i}", level=level, needs_admin_review=needs_admin_review)
        db.session.add(v)
        vocab_list.append(v)
    db.session.commit()
    return vocab_list

def test_exact_five_card_session(user_id, app):
    # Populate 5 vocabularies, force first one to need admin review so replacement logic triggers
    vocab = populate_vocab(level="intermediate", count=5, needs_admin_review=False)
    vocab[0].needs_admin_review = True
    db.session.commit()

    session = create_flashcard_session(user_id, level="intermediate", requested_count=5, order_mode="alphabetical")
    assert session.requested_count == 5
    assert len(session.session_words) == 5
    # Ensure no vocab in session still needs admin review
    for sw in session.session_words:
        assert not sw.vocabulary.needs_admin_review

def test_replacement_fallback_when_no_candidates(user_id, app):
    # No vocabularies at all – create session requesting 5 cards should return empty list
    session = create_flashcard_session(user_id, level="intermediate", requested_count=5, order_mode="alphabetical")
    assert session.requested_count == 5
    assert len(session.session_words) == 0

