from datetime import date, datetime, timedelta

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import QuizHistory, StudySession, UserAppSession, UserWord, Word, db
from app.services.ai_generator import generate_word_content
from app.services.spaced_repetition import get_due_review_words
from app.services.stats import clean_text, get_study_streak, get_weekly_activity, pluralize


def register(app):
    def get_total_active_seconds(user_id):
        return int(
            db.session.query(db.func.coalesce(db.func.sum(UserAppSession.active_seconds), 0))
            .filter(UserAppSession.user_id == user_id)
            .scalar()
            or 0
        )

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
                    "body": "Open the user manual for a short guide to the main VocabAI workflow.",
                    "href": url_for("user_manual"),
                    "label": "Open manual",
                }
            ],
        )

    @app.context_processor
    def inject_onboarding_context():
        excluded_endpoints = {
            "admin_dashboard",
            "admin_logout",
            "admin_update_user_restriction",
            "user_manual",
        }
        if not current_user.is_authenticated or request.endpoint in excluded_endpoints:
            return {
                "show_onboarding_nudge": False,
                "onboarding_tips": [],
                "onboarding_seconds_left": 0,
            }

        active_seconds = get_total_active_seconds(current_user.id)
        show_tips = active_seconds < 1200
        return {
            "show_onboarding_nudge": show_tips,
            "onboarding_tips": get_onboarding_tips(request.endpoint or ""),
            "onboarding_seconds_left": max(0, 1200 - active_seconds),
            "onboarding_minutes_left": max(1, (max(0, 1200 - active_seconds) + 59) // 60),
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
            already_known=False,
        ).count()
        already_known_words = UserWord.query.filter_by(
            user_id=current_user.id,
            already_known=True,
        ).count()
        difficult_words = UserWord.query.filter_by(
            user_id=current_user.id,
            is_difficult=True,
        ).count()
        unlearned_words = UserWord.query.filter_by(
            user_id=current_user.id,
            learned=False,
            already_known=False,
        ).count()
        words_added_today = UserWord.query.filter_by(
            user_id=current_user.id,
            added_date=date.today(),
        ).count()
        learned_today = UserWord.query.filter_by(
            user_id=current_user.id,
            learned_at=date.today(),
            already_known=False,
        ).count()
        words_to_review_today = len(get_due_review_words(current_user.id))
        study_streak = get_study_streak(current_user.id)
        progress_percentage = round(((learned_words + already_known_words) / total_words) * 100) if total_words else 0
        daily_goal = current_user.daily_goal or 10
        daily_goal_percentage = min(100, round((learned_today / daily_goal) * 100)) if daily_goal else 0
        display_name = current_user.display_name
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
            user_words=user_words,
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
            default_study_focus=current_user.default_study_focus or "IELTS preparation words",
            last_session=last_session,
            last_session_remaining=last_session_remaining,
            difficulty_progress=difficulty_progress,
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
        query = clean_text(request.args.get("q")).lower()
        if not query:
            flash("Type a word to search.", "info")
            return redirect(url_for("dashboard"))

        word = Word.query.filter_by(word=query).first()
        if word is None:
            content = generate_word_content(query)
            word = Word(
                word=query,
                meaning=clean_text(content.get("meaning")) or f"A simple meaning for {query}.",
                bangla_meaning=clean_text(content.get("bangla_meaning")) or None,
                phonetic=clean_text(content.get("phonetic")) or None,
                synonym=clean_text(content.get("synonym")) or None,
                memory_trick=clean_text(content.get("memory_trick")) or None,
                topic=clean_text(content.get("topic")) or "general",
                sentence=clean_text(content.get("sentence")) or None,
                created_at=date.today(),
            )
            db.session.add(word)
            db.session.commit()

        return render_template("search.html", word=word, search_query=query)

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
            StudySession.query.filter_by(user_id=current_user.id)
            .order_by(StudySession.created_at.desc(), StudySession.id.desc())
            .all()
        )
        return render_template("sessions.html", study_sessions=study_sessions)

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        if request.method == "POST":
            nickname = clean_text(request.form.get("nickname"))
            current_user.default_study_focus = clean_text(request.form.get("default_study_focus")) or None
            try:
                daily_goal = int(request.form.get("daily_goal", current_user.daily_goal or 10))
            except (TypeError, ValueError):
                daily_goal = current_user.daily_goal or 10
            current_user.nickname = nickname[:80] if nickname else current_user.display_name
            current_user.daily_goal = max(1, min(daily_goal, 100))
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("profile"))

        total_sessions = StudySession.query.filter_by(user_id=current_user.id).count()
        total_words = UserWord.query.filter_by(user_id=current_user.id).count()
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
        return render_template(
            "profile.html",
            total_sessions=total_sessions,
            total_words=total_words,
            total_quizzes=quiz_metrics["total_attempts"],
            latest_quiz=quiz_metrics["latest_quiz"],
            quiz_metrics=quiz_metrics,
            usage_metrics=usage_metrics,
        )
