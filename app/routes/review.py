from flask import jsonify, render_template
from flask_login import current_user, login_required

from app.models import UserWordProgress, db
from app.services.vocabulary_platform import get_review_words, mark_progress_reviewed


def register(app):
    @app.route("/review")
    @login_required
    def review():
        review_words = get_review_words(current_user.id, count=10)
        return render_template(
            "flashcards.html",
            user_words=review_words,
            review_mode=True,
        )

    @app.route("/review/complete/<int:user_word_id>", methods=["POST"])
    @login_required
    def complete_review(user_word_id):
        user_word = UserWordProgress.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        mark_progress_reviewed(user_word)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Marked as reviewed."})
