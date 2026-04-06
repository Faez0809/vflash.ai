from datetime import date

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import QuizHistory, StudySession, UserWord, Word, db
from app.services.ai_generator import generate_word_content
from app.services.spaced_repetition import get_due_review_words
from app.services.stats import clean_text, get_study_streak, get_weekly_activity


def register(app):
    @app.route("/")
    def index():
        return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))

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
            dashboard_messages.append(f"You have {words_to_review_today} words to review today.")
        if study_streak:
            dashboard_messages.append(f"You're on a {study_streak} day streak. Keep going!")
        if difficult_words:
            dashboard_messages.append(f"{difficult_words} difficult words need attention.")
        if daily_goal and learned_today < daily_goal:
            remaining_goal = daily_goal - learned_today
            if remaining_goal <= 3:
                dashboard_messages.append("You're close to your daily goal.")
            else:
                dashboard_messages.append(f"{remaining_goal} more words will complete today's goal.")
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
        total_quizzes = QuizHistory.query.filter_by(user_id=current_user.id).count()
        latest_quiz = (
            QuizHistory.query.filter_by(user_id=current_user.id)
            .order_by(QuizHistory.created_at.desc(), QuizHistory.id.desc())
            .first()
        )
        return render_template(
            "profile.html",
            total_sessions=total_sessions,
            total_words=total_words,
            total_quizzes=total_quizzes,
            latest_quiz=latest_quiz,
        )
