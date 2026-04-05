from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.models import UserWord, Word, db
from app.services.stats import clean_text


def register(app):
    @app.route("/words")
    @login_required
    def words():
        search_query = clean_text(request.args.get("q"))
        difficulty_filter = clean_text(request.args.get("difficulty"))
        topic_filter = clean_text(request.args.get("topic"))
        learned_filter = clean_text(request.args.get("learned"))
        difficult_only = request.args.get("difficult") == "1"
        favorite_only = request.args.get("favorite") == "1"

        user_words_query = UserWord.query.filter_by(user_id=current_user.id).join(Word)

        if search_query:
            search_term = f"%{search_query}%"
            user_words_query = user_words_query.filter(
                or_(
                    Word.word.ilike(search_term),
                    Word.meaning.ilike(search_term),
                    Word.topic.ilike(search_term),
                    Word.difficulty.ilike(search_term),
                )
            )

        if difficulty_filter and difficulty_filter != "All":
            user_words_query = user_words_query.filter(Word.difficulty == difficulty_filter)

        if topic_filter and topic_filter != "All":
            user_words_query = user_words_query.filter(Word.topic == topic_filter)

        if learned_filter == "learned":
            user_words_query = user_words_query.filter(UserWord.learned.is_(True))
        elif learned_filter == "learning":
            user_words_query = user_words_query.filter(UserWord.learned.is_(False))

        if difficult_only:
            user_words_query = user_words_query.filter(UserWord.is_difficult.is_(True))

        if favorite_only:
            user_words_query = user_words_query.filter(UserWord.is_favorite.is_(True))

        user_words = user_words_query.order_by(UserWord.added_date.desc(), Word.word.asc()).all()
        available_topics = [
            row[0]
            for row in (
                db.session.query(Word.topic)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(UserWord.user_id == current_user.id, Word.topic.isnot(None))
                .distinct()
                .order_by(Word.topic.asc())
                .all()
            )
            if row[0]
        ]
        available_difficulties = [
            row[0]
            for row in (
                db.session.query(Word.difficulty)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(UserWord.user_id == current_user.id, Word.difficulty.isnot(None))
                .distinct()
                .order_by(Word.difficulty.asc())
                .all()
            )
            if row[0]
        ]
        return render_template(
            "words.html",
            user_words=user_words,
            available_topics=available_topics,
            available_difficulties=available_difficulties,
            search_query=search_query,
            difficulty_filter=difficulty_filter or "All",
            topic_filter=topic_filter or "All",
            learned_filter=learned_filter or "all",
            difficult_only=difficult_only,
            favorite_only=favorite_only,
        )

    @app.route("/difficult")
    @login_required
    def difficult_words():
        difficult_items = (
            UserWord.query.filter_by(user_id=current_user.id, is_difficult=True)
            .join(Word)
            .order_by(UserWord.added_date.desc(), Word.word.asc())
            .all()
        )
        return render_template("difficult.html", user_words=difficult_items)

    @app.route("/words/favorite/<int:user_word_id>", methods=["POST"])
    @login_required
    def toggle_favorite_flag(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        user_word.is_favorite = not user_word.is_favorite
        db.session.commit()
        flash(
            "Word added to favorites." if user_word.is_favorite else "Word removed from favorites.",
            "success" if user_word.is_favorite else "info",
        )
        next_page = request.form.get("next") or request.referrer or url_for("words")
        return redirect(next_page)

    @app.route("/words/note/<int:user_word_id>", methods=["POST"])
    @login_required
    def save_word_note(user_word_id):
        user_word = UserWord.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()

        user_word.note = clean_text(request.form.get("note")) or None
        db.session.commit()
        flash("Your note has been saved.", "success")
        next_page = request.form.get("next") or request.referrer or url_for("words")
        return redirect(next_page)
