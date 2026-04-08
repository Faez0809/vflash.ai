from flask import jsonify, render_template
from flask_login import current_user, login_required

from app.models import UserWord, db
from app.services.learning_content import enrich_user_word_entries
from app.services.spaced_repetition import clear_due_reviews, get_due_review_words


def register(app):
    @app.route("/review")
    @login_required
    def review():
        review_words = get_due_review_words(current_user.id)
        enrich_user_word_entries(review_words, allow_ai=True)
        return render_template(
            "flashcards.html",
            user_words=review_words,
            review_mode=True,
        )

    @app.route("/review/complete/<int:user_word_id>", methods=["POST"])
    @login_required
    def complete_review(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
            learned=True,
        ).first_or_404()

        clear_due_reviews(user_word)
        db.session.commit()

        return jsonify({"status": "ok", "message": "Marked as reviewed."})
