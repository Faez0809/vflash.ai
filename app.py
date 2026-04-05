from collections import Counter
from datetime import date, timedelta
import os
import secrets

import runtime_compat
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

from ai_generator import generate_vocabulary_words
from models import StudySession, User, UserWord, Word, db


load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
LOCAL_DB_PATH = r"C:\vocabai\vocabai.db"
os.makedirs(INSTANCE_DIR, exist_ok=True)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{LOCAL_DB_PATH}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Database setup
db.init_app(app)


# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def clean_text(value):
    """Normalize optional text fields coming from forms or AI responses."""
    if value is None:
        return ""
    return str(value).strip()


def get_study_streak(user_id):
    """Count consecutive days with study activity ending today."""
    user_activity = UserWord.query.filter_by(user_id=user_id).all()
    activity_dates = {
        activity_date
        for item in user_activity
        for activity_date in (item.added_date, item.last_reviewed)
        if activity_date
    }
    if not activity_dates:
        return 0

    streak = 0
    current_day = date.today()
    while current_day in activity_dates:
        streak += 1
        current_day -= timedelta(days=1)
    return streak


def get_weekly_activity(user_id):
    """Return lightweight activity counts for the last 7 days."""
    user_activity = UserWord.query.filter_by(user_id=user_id).all()
    counts = Counter()
    for item in user_activity:
        for activity_date in (item.added_date, item.last_reviewed):
            if activity_date:
                counts[activity_date] += 1

    today = date.today()
    weekly_activity = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        weekly_activity.append(
            {
                "label": day.strftime("%a"),
                "count": counts.get(day, 0),
            }
        )
    max_count = max((item["count"] for item in weekly_activity), default=0)
    for item in weekly_activity:
        item["height"] = 18 if max_count == 0 else max(18, round((item["count"] / max_count) * 100))
    return weekly_activity


def ensure_word_bangla_meaning_column():
    """Add the bangla_meaning column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("word")}
    if "bangla_meaning" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN bangla_meaning TEXT"))
        db.session.commit()


def ensure_word_difficulty_column():
    """Add the difficulty column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("word")}
    if "difficulty" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN difficulty VARCHAR(20)"))
        db.session.commit()


def ensure_word_part_of_speech_column():
    """Add the part_of_speech column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("word")}
    if "part_of_speech" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN part_of_speech VARCHAR(50)"))
        db.session.commit()


def ensure_user_word_session_id_column():
    """Add the session_id column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("user_word")}
    if "session_id" not in columns:
        db.session.execute(text("ALTER TABLE user_word ADD COLUMN session_id INTEGER"))
        db.session.commit()


def ensure_word_content_columns():
    """Add AI-enriched word columns for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("word")}
    if "bangla_pronunciation" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN bangla_pronunciation TEXT"))
    if "phonetic" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN phonetic TEXT"))
    if "synonym" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN synonym TEXT"))
    if "memory_trick" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN memory_trick TEXT"))
    if "topic" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN topic VARCHAR(120)"))
    if "created_at" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN created_at DATE"))
    db.session.commit()


def ensure_study_session_custom_prompt_column():
    """Add the custom_prompt column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("study_session")}
    if "custom_prompt" not in columns:
        db.session.execute(text("ALTER TABLE study_session ADD COLUMN custom_prompt TEXT"))
        db.session.commit()


def ensure_user_default_study_focus_column():
    """Add the default_study_focus column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("user")}
    if "default_study_focus" not in columns:
        db.session.execute(text("ALTER TABLE user ADD COLUMN default_study_focus TEXT"))
        db.session.commit()


@app.route("/")
def index():
    return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Welcome back.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Store emails in lowercase so login and uniqueness checks stay consistent.
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        else:
            user = User(email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_words = (
        UserWord.query.filter_by(user_id=current_user.id)
        .join(Word)
        .order_by(UserWord.added_date.desc(), Word.word.asc())
        .all()
    )
    total_words = UserWord.query.filter_by(user_id=current_user.id).count()
    learned_words = UserWord.query.filter_by(
        user_id=current_user.id,
        learned=True,
    ).count()
    unlearned_words = UserWord.query.filter_by(
        user_id=current_user.id,
        learned=False,
    ).count()
    words_added_today = UserWord.query.filter_by(
        user_id=current_user.id,
        added_date=date.today(),
    ).count()
    study_streak = get_study_streak(current_user.id)
    progress_percentage = round((learned_words / total_words) * 100) if total_words else 0
    last_session = (
        StudySession.query.filter_by(user_id=current_user.id)
        .order_by(StudySession.created_at.desc(), StudySession.id.desc())
        .first()
    )
    last_session_remaining = 0
    if last_session:
        last_session_remaining = UserWord.query.filter_by(
            user_id=current_user.id,
            session_id=last_session.id,
            learned=False,
        ).count()

    difficulty_counts = {
        "Beginner": 0,
        "Intermediate": 0,
        "Advanced": 0,
    }
    learned_difficulty_counts = {
        "Beginner": 0,
        "Intermediate": 0,
        "Advanced": 0,
    }
    for item in user_words:
        difficulty = item.word_entry.difficulty or "Beginner"
        if difficulty not in difficulty_counts:
            difficulty = "Beginner"
        difficulty_counts[difficulty] += 1
        if item.learned:
            learned_difficulty_counts[difficulty] += 1

    max_difficulty_count = max(difficulty_counts.values(), default=0)
    difficulty_progress = []
    for label in ("Beginner", "Intermediate", "Advanced"):
        total_for_level = difficulty_counts[label]
        learned_for_level = learned_difficulty_counts[label]
        difficulty_progress.append(
            {
                "label": label,
                "count": total_for_level,
                "learned": learned_for_level,
                "fill": 0 if max_difficulty_count == 0 else max(10, round((total_for_level / max_difficulty_count) * 100)),
            }
        )

    recent_words = user_words[:6]
    weekly_activity = get_weekly_activity(current_user.id)

    return render_template(
        "dashboard.html",
        user_words=user_words,
        recent_words=recent_words,
        total_words=total_words,
        learned_words=learned_words,
        unlearned_words=unlearned_words,
        words_added_today=words_added_today,
        study_streak=study_streak,
        progress_percentage=progress_percentage,
        default_study_focus=current_user.default_study_focus or "IELTS preparation words",
        last_session=last_session,
        last_session_remaining=last_session_remaining,
        difficulty_progress=difficulty_progress,
        weekly_activity=weekly_activity,
    )


@app.route("/generate-words", methods=["POST"])
@login_required
def generate_words():
    difficulty = request.form.get("difficulty", "Beginner").strip().title()
    difficulty_map = {
        "Beginner": "Beginner",
        "Medium": "Intermediate",
        "Intermediate": "Intermediate",
        "Hard": "Advanced",
        "Advanced": "Advanced",
    }
    difficulty = difficulty_map.get(difficulty, "Beginner")

    try:
        word_count = int(request.form.get("word_count", "5"))
    except ValueError:
        word_count = 5

    if word_count not in {5, 10, 15}:
        word_count = 5

    custom_prompt = request.form.get("custom_prompt", "").strip()
    save_as_default = request.form.get("save_as_default") == "on"
    effective_prompt = custom_prompt or clean_text(current_user.default_study_focus)

    if save_as_default:
        current_user.default_study_focus = custom_prompt or None

    learned_user_words = {
        row[0]
        for row in (
            db.session.query(Word.word)
            .join(UserWord, UserWord.word_id == Word.id)
            .filter(
                UserWord.user_id == current_user.id,
                UserWord.learned.is_(True),
            )
            .all()
        )
    }
    existing_user_words = {
        row[0]
        for row in (
            db.session.query(Word.word)
            .join(UserWord, UserWord.word_id == Word.id)
            .filter(UserWord.user_id == current_user.id)
            .all()
        )
    }
    generated_words = []
    seen_words = set(existing_user_words)
    attempts = 0
    max_attempts = max(6, word_count * 3)

    while len(generated_words) < word_count and attempts < max_attempts:
        attempts += 1
        remaining = word_count - len(generated_words)
        ai_words = generate_vocabulary_words(
            difficulty=difficulty,
            word_count=remaining,
            user_custom_prompt=effective_prompt,
            avoid_words=sorted(learned_user_words),
        )

        for item in ai_words:
            normalized_word = clean_text(item.get("word")).lower()
            already_exists_for_user = (
                db.session.query(UserWord.id)
                .join(Word, UserWord.word_id == Word.id)
                .filter(
                    UserWord.user_id == current_user.id,
                    Word.word == normalized_word,
                )
                .first()
                is not None
            )
            if not normalized_word or normalized_word in seen_words or already_exists_for_user:
                continue

            item["word"] = normalized_word
            generated_words.append(item)
            seen_words.add(normalized_word)

            if len(generated_words) >= word_count:
                break

    if not generated_words:
        if save_as_default:
            db.session.commit()
        flash("Could not generate new words right now. Please try again.", "error")
        return redirect(url_for("dashboard"))

    study_session = StudySession(
        user_id=current_user.id,
        difficulty=difficulty,
        word_count=len(generated_words),
        custom_prompt=effective_prompt or None,
        created_at=date.today(),
    )
    db.session.add(study_session)
    db.session.flush()
    added_count = 0

    for item in generated_words:
        normalized_word = clean_text(item.get("word")).lower()
        if not normalized_word:
            continue

        word = Word.query.filter_by(word=normalized_word).first()
        part_of_speech = clean_text(item.get("part_of_speech"))
        meaning = clean_text(item.get("meaning"))
        bangla_meaning = clean_text(item.get("bangla_meaning"))
        phonetic = clean_text(item.get("phonetic"))
        synonym = clean_text(item.get("synonym"))
        memory_trick = clean_text(item.get("memory_trick"))
        item_difficulty = clean_text(item.get("difficulty")) or difficulty
        topic = clean_text(item.get("topic")) or (effective_prompt[:120] if effective_prompt else "General")
        sentence = clean_text(item.get("sentence"))

        if word is None:
            word = Word(
                word=normalized_word,
                part_of_speech=part_of_speech or None,
                meaning=meaning,
                bangla_meaning=bangla_meaning or None,
                phonetic=phonetic or None,
                synonym=synonym or None,
                memory_trick=memory_trick or None,
                difficulty=item_difficulty,
                topic=topic or None,
                sentence=sentence,
                created_at=date.today(),
            )
            db.session.add(word)
            db.session.flush()
        else:
            if not word.part_of_speech and part_of_speech:
                word.part_of_speech = part_of_speech
            if not word.meaning and meaning:
                word.meaning = meaning
            if not word.bangla_meaning and bangla_meaning:
                word.bangla_meaning = bangla_meaning
            if not word.phonetic and phonetic:
                word.phonetic = phonetic
            if not word.synonym and synonym:
                word.synonym = synonym
            if not word.memory_trick and memory_trick:
                word.memory_trick = memory_trick
            if not word.difficulty:
                word.difficulty = difficulty
            if not word.topic and topic:
                word.topic = topic
            if not word.sentence and sentence:
                word.sentence = sentence
            if not word.created_at:
                word.created_at = date.today()

        existing_user_word = UserWord.query.filter_by(
            user_id=current_user.id,
            word_id=word.id,
        ).first()
        if existing_user_word:
            continue

        db.session.add(
            UserWord(
                user_id=current_user.id,
                word_id=word.id,
                session_id=study_session.id,
                added_date=date.today(),
                learned=False,
            )
        )
        added_count += 1

    db.session.commit()
    if save_as_default:
        flash("Your default study focus has been updated.", "info")
    if added_count == word_count:
        flash(f"{added_count} new words generated for your study list.", "success")
    elif added_count:
        flash(
            f"{added_count} new words generated. The AI repeated too many existing words before reaching {word_count}.",
            "info",
        )
    else:
        flash("No new words were added because they already exist in your study list.", "info")
    return redirect(url_for("flashcards_session", session_id=study_session.id))


@app.route("/flashcards")
@login_required
def flashcards():
    user_words = (
        UserWord.query.filter_by(user_id=current_user.id)
        .join(Word)
        .filter(UserWord.learned.is_(False))
        .order_by(UserWord.added_date.desc(), Word.word.asc())
        .all()
    )
    return render_template("flashcards.html", user_words=user_words)


@app.route("/generate")
@login_required
def generate_page():
    return redirect(f"{url_for('dashboard')}#generate-section")


@app.route("/words")
@login_required
def words():
    user_words = (
        UserWord.query.filter_by(user_id=current_user.id)
        .join(Word)
        .order_by(UserWord.added_date.desc(), Word.word.asc())
        .all()
    )
    return render_template("words.html", user_words=user_words)


@app.route("/difficult")
@login_required
def difficult_words():
    difficult_items = (
        UserWord.query.filter_by(user_id=current_user.id, learned=False)
        .join(Word)
        .order_by(Word.difficulty.desc(), UserWord.added_date.asc(), Word.word.asc())
        .all()
    )
    return render_template("difficult.html", user_words=difficult_items)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.default_study_focus = clean_text(request.form.get("default_study_focus")) or None
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    total_sessions = StudySession.query.filter_by(user_id=current_user.id).count()
    total_words = UserWord.query.filter_by(user_id=current_user.id).count()
    return render_template(
        "profile.html",
        total_sessions=total_sessions,
        total_words=total_words,
    )


@app.route("/flashcards/session/<int:session_id>")
@login_required
def flashcards_session(session_id):
    study_session = StudySession.query.filter_by(
        id=session_id,
        user_id=current_user.id,
    ).first_or_404()
    user_words = (
        UserWord.query.filter_by(
            user_id=current_user.id,
            session_id=study_session.id,
        )
        .join(Word)
        .filter(UserWord.learned.is_(False))
        .order_by(UserWord.added_date.desc(), Word.word.asc())
        .all()
    )
    return render_template(
        "flashcards.html",
        user_words=user_words,
        study_session=study_session,
    )


@app.route("/sessions")
@login_required
def sessions():
    study_sessions = (
        StudySession.query.filter_by(user_id=current_user.id)
        .order_by(StudySession.created_at.desc(), StudySession.id.desc())
        .all()
    )
    return render_template("sessions.html", study_sessions=study_sessions)


@app.route("/flashcards/learn/<int:user_word_id>", methods=["POST"])
@login_required
def mark_flashcard_learned(user_word_id):
    user_word = UserWord.query.filter_by(
        id=user_word_id,
        user_id=current_user.id,
    ).first_or_404()

    user_word.learned = True
    user_word.last_reviewed = date.today()
    db.session.commit()

    return jsonify({"status": "success"})


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


with app.app_context():
    # Create tables after the app, database, and models are fully configured.
    db.create_all()
    ensure_word_bangla_meaning_column()
    ensure_word_difficulty_column()
    ensure_word_part_of_speech_column()
    ensure_user_word_session_id_column()
    ensure_word_content_columns()
    ensure_study_session_custom_prompt_column()
    ensure_user_default_study_focus_column()


if __name__ == "__main__":
    app.run(debug=True)
