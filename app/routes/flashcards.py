from datetime import date

from flask import jsonify, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app.models import UserWord, Word, db
from app.services.learning_content import enrich_user_word_entries, touch_user_word_interaction
from app.services.spaced_repetition import schedule_word_for_review


def register(app):
    @app.route("/flashcards")
    @login_required
    def flashcards():
        user_words = (
            UserWord.query.options(selectinload(UserWord.word_entry))
            .filter_by(user_id=current_user.id)
            .join(Word)
            .filter(UserWord.learned.is_(False))
            .order_by(UserWord.added_date.desc(), Word.word.asc())
            .all()
        )
        enrich_user_word_entries(user_words, allow_ai=True)
        return render_template("flashcards.html", user_words=user_words)

    @app.route("/flashcards/session/<int:session_id>")
    @login_required
    def flashcards_session(session_id):
        # Session lookup stays explicit so users can only open their own sessions.
        from app.models import StudySession

        study_session = StudySession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
        ).first_or_404()
        user_words = (
            UserWord.query.options(selectinload(UserWord.word_entry))
            .filter_by(
                user_id=current_user.id,
                session_id=study_session.id,
            )
            .join(Word)
            .filter(UserWord.learned.is_(False))
            .order_by(UserWord.added_date.desc(), Word.word.asc())
            .all()
        )
        enrich_user_word_entries(user_words, allow_ai=True)
        return render_template(
            "flashcards.html",
            user_words=user_words,
            study_session=study_session,
        )

    @app.route("/flashcards/learn/<int:user_word_id>", methods=["POST"])
    @login_required
    def mark_flashcard_learned(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        schedule_word_for_review(user_word)
        db.session.commit()

        return jsonify({"status": "ok", "message": "Marked as learned."})

    @app.route("/flashcards/already-known/<int:user_word_id>", methods=["POST"])
    @login_required
    def mark_flashcard_already_known(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        today = date.today()
        user_word.already_known = True
        user_word.learned = True
        user_word.learned_at = user_word.learned_at or today
        user_word.rev1 = None
        user_word.rev2 = None
        user_word.rev3 = None
        user_word.last_reviewed = None
        db.session.commit()

        return jsonify({"status": "ok", "message": "Marked as already known."})

    @app.route("/words/difficult/<int:user_word_id>", methods=["POST"])
    @login_required
    def toggle_difficult_flag(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        user_word.is_difficult = not user_word.is_difficult
        touch_user_word_interaction(user_word)
        db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {
                    "status": "ok",
                    "is_difficult": user_word.is_difficult,
                    "message": "Marked as difficult." if user_word.is_difficult else "Removed from difficult words.",
                }
            )

        flash(
            "Word added to difficult words." if user_word.is_difficult else "Word removed from difficult words.",
            "success" if user_word.is_difficult else "info",
        )
        next_page = request.form.get("next") or request.referrer or url_for("difficult_words")
        return redirect(next_page)
