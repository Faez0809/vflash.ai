from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.models import SearchVocabulary, UserWordProgress, VocabularyMaster, db
from app.services.stats import clean_text
from app.services.vocabulary_platform import get_difficult_progress_words


def register(app):
    @app.route("/words")
    @login_required
    def words():
        search_query = clean_text(request.args.get("q"))
        difficulty_filter = clean_text(request.args.get("difficulty"))
        learned_filter = clean_text(request.args.get("learned"))
        source_filter = clean_text(request.args.get("source")) or "all"
        difficult_only = request.args.get("difficult") == "1"
        favorite_only = request.args.get("favorite") == "1"

        query = (
            UserWordProgress.query.options(
                selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
            )
            .join(VocabularyMaster)
            .filter(UserWordProgress.user_id == current_user.id)
        )
        if source_filter not in {"all", "searched", "curriculum"}:
            source_filter = "all"

        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                or_(
                    VocabularyMaster.word.ilike(search_term),
                    VocabularyMaster.level.ilike(search_term),
                )
            )
        if difficulty_filter and difficulty_filter != "All":
            query = query.filter(VocabularyMaster.level == difficulty_filter)
        if learned_filter == "learned":
            query = query.filter(UserWordProgress.is_learned.is_(True))
        elif learned_filter == "learning":
            query = query.filter(UserWordProgress.is_learned.is_(False))
        if difficult_only:
            query = query.filter(UserWordProgress.is_difficult.is_(True))
        if favorite_only:
            query = query.filter(UserWordProgress.is_favorite.is_(True))

        user_words = []
        if source_filter in {"all", "curriculum"}:
            user_words = query.order_by(UserWordProgress.updated_at.desc(), VocabularyMaster.word.asc()).all()

        searched_query = SearchVocabulary.query.filter(
            SearchVocabulary.searched_by_user_id == current_user.id,
            SearchVocabulary.source_type == "search",
            SearchVocabulary.is_fully_enriched.is_(True),
            SearchVocabulary.enrichment_score >= 0.8,
            SearchVocabulary.definition.isnot(None),
            SearchVocabulary.bangla_meaning.isnot(None),
            SearchVocabulary.example_sentence.isnot(None),
            SearchVocabulary.part_of_speech.isnot(None),
        )
        if search_query:
            search_term = f"%{search_query}%"
            searched_query = searched_query.filter(
                or_(
                    SearchVocabulary.word.ilike(search_term),
                    SearchVocabulary.definition.ilike(search_term),
                    SearchVocabulary.bangla_meaning.ilike(search_term),
                    SearchVocabulary.difficulty_estimate.ilike(search_term),
                )
            )
        if difficulty_filter and difficulty_filter != "All":
            searched_query = searched_query.filter(SearchVocabulary.difficulty_estimate == difficulty_filter)

        searched_words = []
        if source_filter == "searched" or (
            source_filter == "all" and learned_filter == "all" and not difficult_only and not favorite_only
        ):
            searched_words = searched_query.order_by(SearchVocabulary.created_at.desc()).limit(25).all()

        available_difficulties = ["intermediate", "upper_intermediate", "advanced"]
        return render_template(
            "words.html",
            user_words=user_words,
            searched_words=searched_words,
            available_topics=[],
            available_difficulties=available_difficulties,
            lookup_word=None,
            lookup_note=None,
            lookup_status=None,
            lookup_suggestions=[],
            related_words=[],
            requested_part_of_speech=None,
            search_query=search_query,
            difficulty_filter=difficulty_filter or "All",
            source_filter=source_filter,
            learned_filter=learned_filter or "all",
            difficult_only=difficult_only,
            favorite_only=favorite_only,
        )

    @app.route("/difficult")
    @login_required
    def difficult_words():
        return render_template("difficult.html", user_words=get_difficult_progress_words(current_user.id))

    @app.route("/words/favorite/<int:user_word_id>", methods=["POST"])
    @login_required
    def toggle_favorite_flag(user_word_id):
        user_word = UserWordProgress.query.filter_by(
            id=user_word_id,
            user_id=current_user.id,
        ).first_or_404()
        user_word.is_favorite = not user_word.is_favorite
        db.session.commit()
        flash(
            "Word added to favorites." if user_word.is_favorite else "Word removed from favorites.",
            "success" if user_word.is_favorite else "info",
        )
        return redirect(request.form.get("next") or request.referrer or url_for("words"))

