from datetime import date
import os
import secrets

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
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ai_generator import generate_vocabulary_words
from models import User, UserWord, Word, db


load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(INSTANCE_DIR, 'vocabai.db')}",
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


def ensure_word_bangla_meaning_column():
    """Add the bangla_meaning column for existing SQLite databases."""
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("word")}
    if "bangla_meaning" not in columns:
        db.session.execute(text("ALTER TABLE word ADD COLUMN bangla_meaning TEXT"))
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


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        word_text = request.form.get("word", "").strip()
        meaning = request.form.get("meaning", "").strip()
        bangla_meaning = request.form.get("bangla_meaning", "").strip()
        sentence = request.form.get("sentence", "").strip()

        if not word_text or not meaning:
            flash("Word and meaning are required.", "error")
        else:
            # Normalize words to lowercase so the shared word bank stays unique.
            normalized_word = word_text.lower()
            word = Word.query.filter_by(word=normalized_word).first()
            is_new_word = word is None

            try:
                if is_new_word:
                    word = Word(
                        word=normalized_word,
                        meaning=meaning,
                        bangla_meaning=bangla_meaning or None,
                        sentence=sentence,
                    )
                    db.session.add(word)
                    db.session.flush()

                user_word = UserWord(
                    user_id=current_user.id,
                    word_id=word.id,
                    added_date=date.today(),
                )
                db.session.add(user_word)
                db.session.commit()
                flash("Word added to your vocabulary list.", "success")
            except IntegrityError:
                db.session.rollback()
                flash("That word is already in your vocabulary list.", "info")

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
    progress_percentage = round((learned_words / total_words) * 100) if total_words else 0

    return render_template(
        "dashboard.html",
        user_words=user_words,
        total_words=total_words,
        learned_words=learned_words,
        unlearned_words=unlearned_words,
        words_added_today=words_added_today,
        progress_percentage=progress_percentage,
    )


@app.route("/generate-words", methods=["POST"])
@login_required
def generate_words():
    generated_words = generate_vocabulary_words()
    added_count = 0

    for item in generated_words:
        normalized_word = item["word"].strip().lower()
        if not normalized_word:
            continue

        word = Word.query.filter_by(word=normalized_word).first()
        if word is None:
            word = Word(
                word=normalized_word,
                meaning=item["meaning"].strip(),
                bangla_meaning=item.get("bangla_meaning", "").strip() or None,
                sentence=item["sentence"].strip(),
            )
            db.session.add(word)
            db.session.flush()

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
                added_date=date.today(),
                learned=False,
            )
        )
        added_count += 1

    db.session.commit()
    if added_count:
        flash(f"{added_count} new words generated for your study list.", "success")
    else:
        flash("No new words were added because they already exist in your study list.", "info")
    return redirect(url_for("flashcards"))


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


if __name__ == "__main__":
    app.run(debug=True)
