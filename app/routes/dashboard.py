from datetime import date, datetime, timedelta

from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import and_, case, func
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash, generate_password_hash

from app import SEARCH_CACHE_TTL_SECONDS, cache
from app.models import (
    FlashcardSession,
    FlashcardSessionWord,
    QuizHistory,
    SearchHistory,
    SearchVocabulary,
    UserAppSession,
    UserWordProgress,
    VocabularyMaster,
    db,
)
from app.services.learning_content import (
    ensure_starter_pack_for_user,
    get_reference_vocabulary_candidates,
    resolve_vocabulary_lookup,
    touch_user_word_interaction,
)
from app.services.spaced_repetition import get_due_review_word_count
from app.services.stats import (
    VOCAB_QUERY_MESSAGE,
    clean_text,
    get_study_streak,
    get_weekly_activity,
    parse_vocabulary_lookup_query,
    pluralize,
    validate_vocabulary_query,
)
from app.services.vocabulary_platform import (
    cache_search_vocabulary,
    calculate_level_progress,
    normalize_vocab_text,
)


def register(app):
    search_cache_key = "search:candidate_words:v1"

    def available_topic_suggestions(user_id, limit=6):
        return ["alphabetical", "mixed"][:limit]

    def get_total_active_seconds(user_id):
        return int(
            db.session.query(db.func.coalesce(db.func.sum(UserAppSession.active_seconds), 0))
            .filter(UserAppSession.user_id == user_id)
            .scalar()
            or 0
        )

    def get_search_candidate_words():
        cached_words = cache.get(search_cache_key)
        if cached_words is not None:
            return cached_words

        fresh_words = get_reference_vocabulary_candidates()
        cache.set(search_cache_key, fresh_words, timeout=SEARCH_CACHE_TTL_SECONDS)  # Global-only cache with finite TTL.
        return fresh_words

    def get_onboarding_tips(endpoint):
        tips_by_endpoint = {
            "dashboard": [
                {
                    "icon": "neurology",
                    "title": "Start here",
                    "body": "Generate your first word set.",
                    "href": url_for("dashboard") + "#generate-section",
                    "label": "Generate words",
                },
                {
                    "icon": "menu_book",
                    "title": "Read the guide",
                    "body": "See the learning flow in one place.",
                    "href": url_for("user_manual"),
                    "label": "Open manual",
                },
                {
                    "icon": "style",
                    "title": "Open Word Lists",
                    "body": "Your saved words will appear here.",
                    "href": url_for("words"),
                    "label": "Open Word Lists",
                },
            ],
            "words": [
                {
                    "icon": "style",
                    "title": "No words yet?",
                    "body": "Generate a study set first.",
                    "href": url_for("dashboard") + "#generate-section",
                    "label": "Generate words",
                },
                {
                    "icon": "menu_book",
                    "title": "Use this page",
                    "body": "Check meanings and manage saved words.",
                    "href": url_for("user_manual"),
                    "label": "Read manual",
                },
            ],
            "flashcards": [
                {
                    "icon": "amp_stories",
                    "title": "Study with cards",
                    "body": "Learn one word at a time.",
                    "href": url_for("flashcards"),
                    "label": "Open flashcards",
                },
                {
                    "icon": "play_arrow",
                    "title": "Need a set first?",
                    "body": "Generate words, then come back here.",
                    "href": url_for("dashboard") + "#generate-section",
                    "label": "Generate first set",
                },
            ],
            "flashcards_session": [
                {
                    "icon": "touch_app",
                    "title": "How to use this",
                    "body": "Mark each word as learned, known, or difficult.",
                    "href": url_for("user_manual"),
                    "label": "See study guide",
                },
            ],
            "review": [
                {
                    "icon": "history",
                    "title": "Review daily",
                    "body": "Revisit words that are due today.",
                    "href": url_for("review"),
                    "label": "Open review",
                },
                {
                    "icon": "menu_book",
                    "title": "Need help?",
                    "body": "See how review fits into your routine.",
                    "href": url_for("user_manual"),
                    "label": "Read manual",
                },
            ],
            "review_session": [
                {
                    "icon": "task_alt",
                    "title": "Finish the queue",
                    "body": "Go through due words one by one.",
                    "href": url_for("user_manual"),
                    "label": "See review tips",
                },
            ],
            "quiz": [
                {
                    "icon": "quiz",
                    "title": "Check your progress",
                    "body": "Use quizzes after studying.",
                    "href": url_for("quiz"),
                    "label": "Start a quiz",
                },
                {
                    "icon": "menu_book",
                    "title": "Need help first?",
                    "body": "See quiz types and when to use them.",
                    "href": url_for("user_manual"),
                    "label": "Open manual",
                },
            ],
            "quiz_start": [
                {
                    "icon": "lightbulb",
                    "title": "Quick tip",
                    "body": "Use the quiz to learn, not only to score.",
                    "href": url_for("user_manual"),
                    "label": "See quiz guide",
                },
            ],
            "profile": [
                {
                    "icon": "person",
                    "title": "Set your defaults",
                    "body": "Update your nickname, focus, and daily goal.",
                    "href": url_for("profile"),
                    "label": "Update profile",
                },
                {
                    "icon": "insights",
                    "title": "Track progress",
                    "body": "See your activity and quiz progress here.",
                    "href": url_for("user_manual"),
                    "label": "Learn more",
                },
            ],
            "search_word": [
                {
                    "icon": "search",
                    "title": "Search anything",
                    "body": "Find a meaning without starting a full session.",
                    "href": url_for("user_manual"),
                    "label": "See search tips",
                },
            ],
        }
        return tips_by_endpoint.get(
            endpoint,
            [
                {
                    "icon": "menu_book",
                    "title": "Quick help",
                    "body": "Open the user manual for a short guide to the main vflash.ai workflow.",
                    "href": url_for("user_manual"),
                    "label": "Open manual",
                }
            ],
        )

    @app.context_processor
    def inject_onboarding_context():
        return {
            "show_onboarding_nudge": False,
            "onboarding_tips": [],
            "onboarding_seconds_left": 0,
            "onboarding_minutes_left": 0,
        }

    def build_quiz_profile_metrics(quiz_history):
        total_attempts = len(quiz_history)
        quit_attempts = sum(1 for item in quiz_history if getattr(item, "was_quit", False))
        completed_attempts = total_attempts - quit_attempts

        completed_history = [item for item in quiz_history if not getattr(item, "was_quit", False)]
        accuracy_attempts = [
            item for item in completed_history
            if (getattr(item, "answered_questions", 0) or item.total_questions) > 0
        ]

        correct_answers = sum(item.score for item in accuracy_attempts)
        answered_questions = sum(
            (getattr(item, "answered_questions", 0) or item.total_questions)
            for item in accuracy_attempts
        )
        configured_questions = sum(
            (getattr(item, "configured_total_questions", 0) or item.total_questions)
            for item in quiz_history
        )

        best_quiz = None
        if completed_history:
            best_quiz = max(
                completed_history,
                key=lambda item: (
                    0 if (getattr(item, "answered_questions", 0) or item.total_questions) == 0
                    else item.score / (getattr(item, "answered_questions", 0) or item.total_questions),
                    item.score,
                    item.id,
                ),
            )

        return {
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "quit_attempts": quit_attempts,
            "completion_rate": round((completed_attempts / total_attempts) * 100) if total_attempts else 0,
            "accuracy": round((correct_answers / answered_questions) * 100) if answered_questions else 0,
            "correct_answers": correct_answers,
            "answered_questions": answered_questions,
            "configured_questions": configured_questions,
            "average_score": round((sum(item.score for item in completed_history) / completed_attempts), 1) if completed_attempts else 0,
            "best_score": best_quiz.score if best_quiz else 0,
            "best_total": (
                getattr(best_quiz, "answered_questions", 0) or best_quiz.total_questions
            ) if best_quiz else 0,
            "latest_quiz": quiz_history[0] if quiz_history else None,
        }

    def build_usage_metrics(app_sessions):
        total_visits = len(app_sessions)
        total_active_seconds = sum(item.active_seconds or 0 for item in app_sessions)
        total_page_views = sum(item.page_views or 0 for item in app_sessions)
        total_interactions = sum(item.interaction_count or 0 for item in app_sessions)
        active_days = len({item.visit_date for item in app_sessions if item.visit_date})
        average_active_minutes = round((total_active_seconds / 60 / total_visits), 1) if total_visits else 0
        recent_threshold = datetime.utcnow() - timedelta(days=7)
        visits_last_7_days = sum(1 for item in app_sessions if item.started_at and item.started_at >= recent_threshold)
        most_recent_session = app_sessions[0] if app_sessions else None

        return {
            "total_visits": total_visits,
            "active_days": active_days,
            "total_active_seconds": total_active_seconds,
            "total_active_minutes": round(total_active_seconds / 60),
            "average_active_minutes": average_active_minutes,
            "total_page_views": total_page_views,
            "total_interactions": total_interactions,
            "visits_last_7_days": visits_last_7_days,
            "last_seen_at": most_recent_session.last_active_at if most_recent_session else None,
            "longest_session_minutes": round(max((item.active_seconds for item in app_sessions), default=0) / 60),
        }

    @app.route("/")
    def index():
        return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))

    @app.route("/manual")
    @login_required
    def user_manual():
        return render_template("manual.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        today = date.today()
        stats_row = (
            db.session.query(
                func.count(UserWordProgress.id),
                func.coalesce(
                    func.sum(case((UserWordProgress.is_learned.is_(True), 1), else_=0)),
                    0,
                ),
                0,
                func.coalesce(func.sum(case((UserWordProgress.is_difficult.is_(True), 1), else_=0)), 0),
                func.coalesce(
                    func.sum(case((UserWordProgress.is_learned.is_(False), 1), else_=0)),
                    0,
                ),
                func.coalesce(
                    func.sum(case((func.date(UserWordProgress.created_at) == today, 1), else_=0)),
                    0,
                ),
                func.coalesce(
                    func.sum(case((and_(UserWordProgress.is_learned.is_(True), func.date(UserWordProgress.updated_at) == today), 1), else_=0)),
                    0,
                ),
            )
            .filter(UserWordProgress.user_id == current_user.id)
            .one()
        )
        (
            total_words,
            learned_words,
            already_known_words,
            difficult_words,
            unlearned_words,
            words_added_today,
            learned_today,
        ) = [int(value or 0) for value in stats_row]
        level_progress = calculate_level_progress(current_user.id)
        words_to_review_today = sum(item["review_queue"] for item in level_progress.values())
        study_streak = get_study_streak(current_user.id)
        progress_percentage = round(((learned_words + already_known_words) / total_words) * 100) if total_words else 0
        daily_goal = current_user.daily_goal or 10
        daily_goal_percentage = min(100, round((learned_today / daily_goal) * 100)) if daily_goal else 0
        display_name = current_user.display_name
        last_session = (
            FlashcardSession.query.filter_by(user_id=current_user.id)
            .order_by(FlashcardSession.created_at.desc(), FlashcardSession.id.desc())
            .first()
        )
        last_session_remaining = 0
        if last_session:
            last_session_remaining = (
                db.session.query(func.count(UserWordProgress.id))
                .join(FlashcardSessionWord, FlashcardSessionWord.vocabulary_id == UserWordProgress.vocabulary_id)
                .filter(
                    UserWordProgress.user_id == current_user.id,
                    UserWordProgress.is_learned.is_(False),
                    FlashcardSessionWord.session_id == last_session.id,
                )
                .scalar()
                or 0
            )

        max_difficulty_count = max((item["total_words"] for item in level_progress.values()), default=0)
        difficulty_progress = []
        curriculum_progress = []
        for label in ("intermediate", "upper_intermediate", "advanced"):
            total_for_level = level_progress[label]["total_words"]
            learned_for_level = level_progress[label]["learned"]
            curriculum_progress.append({"label": label, **level_progress[label]})
            difficulty_progress.append(
                {
                    "label": label,
                    "count": total_for_level,
                    "learned": learned_for_level,
                    "fill": 0 if max_difficulty_count == 0 else max(10, round((total_for_level / max_difficulty_count) * 100)),
                }
            )

        recent_words = (
            UserWordProgress.query.options(
                selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
            )
            .filter_by(user_id=current_user.id)
            .order_by(UserWordProgress.updated_at.desc(), UserWordProgress.id.desc())
            .limit(6)
            .all()
        )
        weekly_activity = get_weekly_activity(current_user.id)
        last_search_topic = clean_text(session.get("last_search_topic"))
        default_study_focus = clean_text(current_user.default_study_focus)
        initial_generate_topic = default_study_focus or last_search_topic
        topic_suggestions = []
        seen_topics = set()
        for candidate in [
            default_study_focus,
            last_search_topic,
            "IELTS preparation",
            "Business English",
            "Academic writing",
            "Daily conversation",
            "Travel English",
        ]:
            cleaned_candidate = clean_text(candidate)
            lowered_candidate = cleaned_candidate.lower()
            if not cleaned_candidate or lowered_candidate in seen_topics:
                continue
            seen_topics.add(lowered_candidate)
            topic_suggestions.append(cleaned_candidate)
        for topic in available_topic_suggestions(current_user.id, limit=6):
            lowered_topic = topic.lower()
            if lowered_topic in seen_topics:
                continue
            seen_topics.add(lowered_topic)
            topic_suggestions.append(topic)
        dashboard_messages = []

        if words_to_review_today:
            dashboard_messages.append(f"You have {pluralize(words_to_review_today, 'word')} to review today.")
        if study_streak:
            dashboard_messages.append(f"You're on a {pluralize(study_streak, 'day')} streak. Keep going!")
        if difficult_words:
            dashboard_messages.append(f"{pluralize(difficult_words, 'difficult word')} need attention.")
        if daily_goal and learned_today < daily_goal:
            remaining_goal = daily_goal - learned_today
            if remaining_goal <= 3:
                dashboard_messages.append("You're close to your daily goal.")
            else:
                dashboard_messages.append(f"{pluralize(remaining_goal, 'more word')} will complete today's goal.")
        if not dashboard_messages:
            dashboard_messages.append("Start a new study set to keep your vocabulary momentum moving.")

        return render_template(
            "dashboard.html",
            display_name=display_name,
            recent_words=recent_words,
            total_words=total_words,
            learned_words=learned_words,
            already_known_words=already_known_words,
            difficult_words=difficult_words,
            unlearned_words=unlearned_words,
            words_added_today=words_added_today,
            learned_today=learned_today,
            words_to_review_today=words_to_review_today,
            study_streak=study_streak,
            progress_percentage=progress_percentage,
            daily_goal=daily_goal,
            daily_goal_percentage=daily_goal_percentage,
            default_study_focus=default_study_focus,
            initial_generate_topic=initial_generate_topic,
            show_default_topic_tip=not bool(default_study_focus) and bool(last_search_topic),
            topic_suggestions=topic_suggestions[:8],
            last_session=last_session,
            last_session_remaining=last_session_remaining,
            difficulty_progress=difficulty_progress,
            curriculum_progress=curriculum_progress,
            weekly_activity=weekly_activity,
            dashboard_messages=dashboard_messages[:3],
        )

    @app.route("/generate")
    @login_required
    def generate_page():
        return redirect(f"{url_for('dashboard')}#generate-section")

    @app.route("/search")
    @login_required
    def search_word():
        from flask import current_app, render_template, request, session, flash, redirect, url_for
        from flask_login import current_user
        import os
        import re
        from difflib import get_close_matches
        from datetime import datetime
        from app.models import db, SearchVocabulary, VocabularyMaster, VocabularyEnrichment, SearchHistory
        from app.services.enrichment_engine import generate_enrichment_payload, calculate_quality_score as engine_score
        from app.services.vocabulary_platform import normalize_level, is_phrase, apply_enrichment_audit, normalize_vocab_text
        try:
            from wordfreq import top_n_list, zipf_frequency
        except ImportError:
            top_n_list = None
            zipf_frequency = None

        SEARCH_WORD_PATTERN = re.compile(r"^[a-z]+(?:'[a-z]+)?$")
        INAPPROPRIATE_SEARCH_WORDS = {
            "anal",
            "anus",
            "arse",
            "asshole",
            "bastard",
            "bitch",
            "bollocks",
            "boner",
            "bullshit",
            "clit",
            "cock",
            "cocksucker",
            "crap",
            "cunt",
            "dick",
            "dildo",
            "dyke",
            "fag",
            "faggot",
            "fuck",
            "fucker",
            "fucking",
            "goddamn",
            "hell",
            "homo",
            "jerkoff",
            "nigga",
            "nigger",
            "penis",
            "piss",
            "porn",
            "pussy",
            "rape",
            "rapist",
            "sex",
            "shit",
            "slut",
            "twat",
            "vagina",
            "whore",
        }

        def normalize_query(q):
            if not q:
                return ""
            return normalize_vocab_text(q)

        def is_valid_english_word(q):
            if not q or not SEARCH_WORD_PATTERN.fullmatch(q):
                return False
            if q in INAPPROPRIATE_SEARCH_WORDS:
                return False
            if len(q) > 30 or re.search(r"(.)\1{3,}", q):
                return False
            if zipf_frequency is None:
                return VocabularyMaster.query.filter_by(normalized_word=q).first() is not None
            return zipf_frequency(q, "en") >= 2.0

        def suggestion_candidates():
            candidates = {
                row[0]
                for row in db.session.query(VocabularyMaster.normalized_word).distinct().all()
                if row[0] and SEARCH_WORD_PATTERN.fullmatch(row[0]) and row[0] not in INAPPROPRIATE_SEARCH_WORDS
            }
            candidates.update(
                row[0]
                for row in db.session.query(SearchVocabulary.normalized_word)
                .filter(SearchVocabulary.enrichment_score >= 0.8, SearchVocabulary.is_fully_enriched.is_(True))
                .distinct()
                .all()
                if row[0] and SEARCH_WORD_PATTERN.fullmatch(row[0]) and row[0] not in INAPPROPRIATE_SEARCH_WORDS
            )
            if top_n_list is not None:
                try:
                    candidates.update(
                        word
                        for word in top_n_list("en", 50000)
                        if SEARCH_WORD_PATTERN.fullmatch(word) and word not in INAPPROPRIATE_SEARCH_WORDS
                    )
                except Exception as exc:
                    current_app.logger.warning(f"Unable to load wordfreq suggestion list: {exc}")
            return sorted(candidates)

        def closest_english_suggestions(q):
            if not q or q in INAPPROPRIATE_SEARCH_WORDS:
                return []
            matches = get_close_matches(q, suggestion_candidates(), n=5, cutoff=0.72)
            return [word for word in matches if word != q and is_valid_english_word(word)][:5]

        class RuntimeWord:
            def __init__(self, payload, norm_q):
                self.word = payload.get("word") or norm_q
                self.part_of_speech = payload.get("part_of_speech") or ""
                self.meaning = payload.get("definition") or ""
                self.definition = payload.get("definition") or ""
                self.bangla_meaning = payload.get("bangla_meaning") or ""
                self.phonetic = payload.get("pronunciation") or ""
                self.synonym = payload.get("synonyms") or ""
                self.synonyms = payload.get("synonyms") or ""
                self.synonym_hint = payload.get("synonyms") or ""
                self.antonyms = payload.get("antonyms") or ""
                self.antonym_hint = payload.get("antonyms") or ""
                self.sentence = payload.get("example_sentence") or ""
                self.example_sentence = payload.get("example_sentence") or ""
                self.topic = payload.get("difficulty") or "general"

        def create_runtime_word_object(payload, norm_q):
            return RuntimeWord(payload, norm_q)

        def calculate_quality_score(payload, norm_q):
            raw_score = engine_score(payload.get("word") or norm_q, payload)
            return raw_score / 100.0

        def required_fields_exist(payload):
            definition = payload.get("definition") or ""
            bangla_meaning = payload.get("bangla_meaning") or ""
            example_sentence = payload.get("example_sentence") or ""
            part_of_speech = payload.get("part_of_speech") or ""
            return bool(
                definition.strip() and
                bangla_meaning.strip() and
                example_sentence.strip() and
                part_of_speech.strip()
            )

        def generate_live_search_payload(query):
            import app.services.groq_provider as groq_provider

            api_key = groq_provider.get_search_key()
            return generate_enrichment_payload(
                query,
                api_key=api_key,
                model="llama-3.1-8b-instant",
                timeout=12,
            )

        def persist_search_vocabulary(payload, norm_q, score):
            try:
                word_val = payload.get("word") or norm_q
                definition = payload.get("definition") or ""
                bangla_meaning = payload.get("bangla_meaning") or ""
                pronunciation = payload.get("pronunciation") or ""
                example_sentence = payload.get("example_sentence") or ""
                synonyms = payload.get("synonyms") or ""
                antonyms = payload.get("antonyms") or ""
                part_of_speech = payload.get("part_of_speech") or ""
                difficulty = payload.get("difficulty") or "intermediate"

                existing_sv = SearchVocabulary.query.filter_by(normalized_word=norm_q).first()
                if existing_sv:
                    existing_sv.definition = definition
                    existing_sv.bangla_meaning = bangla_meaning
                    existing_sv.pronunciation = pronunciation
                    existing_sv.synonyms = synonyms
                    existing_sv.antonyms = antonyms
                    existing_sv.example_sentence = example_sentence
                    existing_sv.part_of_speech = part_of_speech
                    existing_sv.enrichment_score = score
                    existing_sv.is_fully_enriched = True
                else:
                    new_sv = SearchVocabulary(
                        word=word_val,
                        normalized_word=norm_q,
                        searched_by_user_id=current_user.id,
                        definition=definition,
                        bangla_meaning=bangla_meaning,
                        pronunciation=pronunciation,
                        synonyms=synonyms,
                        antonyms=antonyms,
                        example_sentence=example_sentence,
                        part_of_speech=part_of_speech,
                        difficulty_estimate=difficulty,
                        source_type="search",
                        ai_generated=True,
                        enrichment_score=score,
                        is_fully_enriched=True
                    )
                    db.session.add(new_sv)

                vocab = VocabularyMaster.query.filter_by(normalized_word=norm_q).first()
                if not vocab:
                    vocab = VocabularyMaster(
                        word=word_val,
                        normalized_word=norm_q,
                        level=normalize_level(difficulty),
                        is_phrase=is_phrase(norm_q),
                    )
                    db.session.add(vocab)
                    db.session.flush()

                if vocab and not vocab.enrichment:
                    enrichment = VocabularyEnrichment(
                        vocabulary_id=vocab.id,
                        definition=definition,
                        bangla_meaning=bangla_meaning,
                        pronunciation=pronunciation,
                        synonyms=synonyms,
                        antonyms=antonyms,
                        example_sentence=example_sentence,
                        part_of_speech=part_of_speech,
                        enrichment_quality_score=int(score * 100),
                        generation_timestamp=datetime.utcnow(),
                        generated_by_model=os.environ.get("GROQ_MODEL") or "llama-3.3-70b-versatile",
                        corrected_manually=False,
                        generated_at=datetime.utcnow(),
                    )
                    apply_enrichment_audit(vocab, enrichment)
                    db.session.add(enrichment)
                    db.session.flush()
                    vocab.enrichment = enrichment

                db.session.add(
                    SearchHistory(
                        user_id=current_user.id,
                        search_query=norm_q,
                        matched_vocabulary_id=vocab.id if vocab else None,
                    )
                )
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error persisting search vocabulary for '{norm_q}': {e}")

        # Execute Search Request Flow
        raw_q = request.args.get("q")
        if not raw_q:
            flash("Please enter a word or phrase to search.", "error")
            return redirect(url_for("dashboard"))

        query = normalize_query(raw_q)
        if not query:
            flash("Please enter a valid word or phrase.", "error")
            return redirect(url_for("dashboard"))

        session["last_search_topic"] = query

        try:
            valid_english_word = is_valid_english_word(query)
            if not valid_english_word:
                return render_template(
                    "search_result.html",
                    word=None,
                    search_query=query,
                    lookup_status="invalid",
                    lookup_suggestions=closest_english_suggestions(query),
                    related_words=[],
                    requested_part_of_speech=None,
                    resolved_query=None,
                    autocorrected_from=None,
                )

            payload = generate_live_search_payload(query)
            rendered_word = create_runtime_word_object(payload, query)
            score = calculate_quality_score(payload, query)

            if valid_english_word and score >= 0.8 and required_fields_exist(payload):
                persist_search_vocabulary(payload, query, score)

            return render_template(
                "search_result.html",
                word=rendered_word,
                search_query=query,
                lookup_status="generated",
                lookup_suggestions=[],
                related_words=[],
                requested_part_of_speech=None,
                resolved_query=query,
                autocorrected_from=None,
            )
        except Exception as exc:
            current_app.logger.exception(f"Direct AI search generation failed for '{query}': {exc}")
            return render_template("search_unavailable.html", query=query, search_query=query)

    @app.route("/usage/ping", methods=["POST"])
    @login_required
    def usage_ping():
        payload = request.get_json(silent=True) or {}
        session_key = clean_text(payload.get("session_key"))[:80]
        page_path = clean_text(payload.get("page_path"))[:255] or request.path

        if not session_key:
            return jsonify({"status": "error", "message": "Missing session key."}), 400

        try:
            active_seconds = int(payload.get("active_seconds", 0))
        except (TypeError, ValueError):
            active_seconds = 0
        try:
            interaction_count = int(payload.get("interaction_count", 0))
        except (TypeError, ValueError):
            interaction_count = 0

        active_seconds = max(0, min(active_seconds, 60))
        interaction_count = max(0, min(interaction_count, 500))
        page_load = bool(payload.get("page_load"))
        now = datetime.utcnow()

        usage_session = UserAppSession.query.filter_by(
            user_id=current_user.id,
            session_key=session_key,
        ).first()

        if usage_session is None:
            usage_session = UserAppSession(
                user_id=current_user.id,
                session_key=session_key,
                visit_date=date.today(),
                started_at=now,
                last_active_at=now,
                active_seconds=0,
                page_views=0,
                interaction_count=0,
                first_path=page_path,
                last_path=page_path,
            )
            db.session.add(usage_session)

        usage_session.last_active_at = now
        usage_session.last_path = page_path
        if not usage_session.first_path:
            usage_session.first_path = page_path
        if page_load:
            usage_session.page_views += 1
        if active_seconds:
            usage_session.active_seconds += active_seconds
        if interaction_count:
            usage_session.interaction_count += interaction_count

        db.session.commit()
        return jsonify({"status": "ok"})

    @app.route("/sessions")
    @login_required
    def sessions():
        study_sessions = (
            FlashcardSession.query.filter_by(user_id=current_user.id)
            .order_by(FlashcardSession.created_at.desc(), FlashcardSession.id.desc())
            .all()
        )
        return render_template("sessions.html", study_sessions=study_sessions)

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if request.method == "POST":
            action = request.form.get("action", "profile").strip().lower()
            if action == "password":
                current_password = request.form.get("current_password", "")
                new_password = request.form.get("new_password", "")
                confirm_password = request.form.get("confirm_password", "")

                if not check_password_hash(current_user.password, current_password):
                    flash("Current password is incorrect.", "error")
                elif len(new_password) < 8:
                    flash("New password must be at least 8 characters long.", "error")
                elif new_password != confirm_password:
                    flash("New passwords do not match.", "error")
                elif check_password_hash(current_user.password, new_password):
                    flash("Choose a new password different from your current one.", "error")
                else:
                    current_user.password = generate_password_hash(new_password)
                    db.session.commit()
                    login_user(current_user, remember=True)
                    flash("Password updated successfully.", "success")
            else:
                nickname = clean_text(request.form.get("nickname"))
                try:
                    daily_goal = int(request.form.get("daily_goal", current_user.daily_goal or 10))
                except (TypeError, ValueError):
                    daily_goal = current_user.daily_goal or 10
                current_user.nickname = nickname[:80] if nickname else current_user.display_name
                current_user.daily_goal = max(1, min(daily_goal, 100))
                db.session.commit()
                flash("Profile updated successfully.", "success")
            return redirect(url_for("profile"))

        total_sessions = FlashcardSession.query.filter_by(user_id=current_user.id).count()
        total_words = UserWordProgress.query.filter_by(user_id=current_user.id).count()
        level_progress = calculate_level_progress(current_user.id)
        curriculum_progress = [
            {"label": label, **level_progress[label]}
            for label in ("intermediate", "upper_intermediate", "advanced")
        ]
        total_generated = sum(item["generated"] for item in level_progress.values())
        total_learned = sum(item["learned"] for item in level_progress.values())
        total_curated_words = sum(item["total_words"] for item in level_progress.values())
        overall_completion = round((total_learned / total_curated_words) * 100, 1) if total_curated_words else 0
        study_streak = get_study_streak(current_user.id)
        quiz_history = (
            QuizHistory.query.filter_by(user_id=current_user.id)
            .order_by(QuizHistory.created_at.desc(), QuizHistory.id.desc())
            .all()
        )
        app_sessions = (
            UserAppSession.query.filter_by(user_id=current_user.id)
            .order_by(UserAppSession.last_active_at.desc(), UserAppSession.id.desc())
            .all()
        )
        quiz_metrics = build_quiz_profile_metrics(quiz_history)
        usage_metrics = build_usage_metrics(app_sessions)
        weekly_activity = get_weekly_activity(current_user.id)
        return render_template(
            "profile.html",
            total_sessions=total_sessions,
            total_words=total_words,
            total_quizzes=quiz_metrics["total_attempts"],
            latest_quiz=quiz_metrics["latest_quiz"],
            quiz_metrics=quiz_metrics,
            usage_metrics=usage_metrics,
            weekly_activity=weekly_activity,
            curriculum_progress=curriculum_progress,
            total_generated=total_generated,
            total_learned=total_learned,
            total_curated_words=total_curated_words,
            overall_completion=overall_completion,
            study_streak=study_streak,
        )
