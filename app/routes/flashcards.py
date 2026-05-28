from flask import jsonify, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required

from app.models import FlashcardSession, UserWordProgress, db
from app.services.vocabulary_platform import (
    get_all_generated_progress_words,
    get_session_progress_words,
    mark_progress_learned,
    is_session_generation_complete,
)


def register(app):
    @app.route("/flashcards")
    @login_required
    def flashcards():
        user_words = [item for item in get_all_generated_progress_words(current_user.id) if not item.is_learned]
        return render_template("flashcards.html", user_words=user_words)

    @app.route("/flashcards/session/<int:session_id>")
    @login_required
    def flashcards_session(session_id):
        study_session = FlashcardSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
        ).first_or_404()
        user_words = get_session_progress_words(current_user.id, session_id)
        return render_template(
            "flashcards.html",
            user_words=user_words,
            study_session=study_session,
        )

    @app.route("/flashcards/learn/<int:user_word_id>", methods=["POST"])
    @login_required
    def mark_flashcard_learned(user_word_id):
        user_word = UserWordProgress.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()
        mark_progress_learned(user_word)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Marked as learned."})

    @app.route("/flashcards/already-known/<int:user_word_id>", methods=["POST"])
    @login_required
    def mark_flashcard_already_known(user_word_id):
        user_word = UserWordProgress.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()
        mark_progress_learned(user_word)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Marked as already known."})

    @app.route("/words/difficult/<int:user_word_id>", methods=["POST"])
    @login_required
    def toggle_difficult_flag(user_word_id):
        user_word = UserWordProgress.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        user_word.is_difficult = not user_word.is_difficult
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

    @app.route("/flashcards/session/<int:session_id>/poll")
    @login_required
    def flashcards_session_poll(session_id):
        study_session = FlashcardSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
        ).first_or_404()
        user_words = get_session_progress_words(current_user.id, session_id, include_learned=False)

        ready_cards = []
        for item in user_words:
            enrich = item.vocabulary.enrichment if item.vocabulary else None
            if enrich is not None and enrich.definition:
                ready_cards.append({
                    "id": item.id,
                    "word": item.vocabulary.word,
                    "is_difficult": item.is_difficult,
                    "already_known": item.already_known,
                    "part_of_speech": enrich.part_of_speech or "",
                    "meaning": enrich.definition,
                    "bangla_meaning": enrich.bangla_meaning or "",
                    "sentence": enrich.example_sentence or "",
                    "phonetic": enrich.pronunciation or "",
                    "synonym": enrich.synonyms or "",
                    "antonym": enrich.antonyms or "",
                })

        completed = is_session_generation_complete(study_session)
        return jsonify({
            "completed": completed,
            "cards": ready_cards,
            # Let the frontend know the original target and how many are ready.
            # Used to correctly adjust the progress counter when some words
            # permanently fail enrichment (needs_admin_review).
            "requested_count": study_session.requested_count,
            "ready_count": len(ready_cards),
        })
