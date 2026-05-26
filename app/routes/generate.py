from flask import flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.models import db
from app.services.stats import pluralize
from app.services.vocabulary_platform import create_flashcard_session, normalize_level, normalize_order_mode


def register(app):
    @app.route("/generate-words", methods=["POST"])
    @login_required
    def generate_words():
        try:
            level = normalize_level(request.form.get("difficulty", "intermediate"))
            order_mode = normalize_order_mode(request.form.get("order_mode", "mixed"))
            try:
                requested_count = int(request.form.get("word_count", "5"))
            except (TypeError, ValueError):
                requested_count = 5
            requested_count = 10 if requested_count == 10 else 5
            include_generated = request.form.get("include_generated") == "1"

            session = create_flashcard_session(
                user_id=current_user.id,
                level=level,
                requested_count=requested_count,
                order_mode=order_mode,
                include_generated=include_generated,
            )
            if session.generated_count == 0:
                db.session.rollback()
                flash("No unseen curated words remain for this level right now.", "info")
                return redirect(f"{url_for('dashboard')}#generate-section")

            db.session.commit()
            flash(f"{pluralize(session.generated_count, 'curated word')} prepared for this session.", "success")
            return redirect(url_for("flashcards_session", session_id=session.id))
        except Exception:
            db.session.rollback()
            flash("We could not prepare a structured flashcard session right now.", "error")
            return redirect(f"{url_for('dashboard')}#generate-section")
