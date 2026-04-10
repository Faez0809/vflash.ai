import secrets
from datetime import date, datetime, timedelta
from functools import wraps
from hmac import compare_digest

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user
from app.models import QuizHistory, User, UserAppSession, UserWord, db


def register(app):
    def get_admin_email():
        return (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()

    def get_admin_password():
        return current_app.config.get("ADMIN_PASSWORD") or ""

    def matches_admin_credentials(email, password):
        admin_email = get_admin_email()
        admin_password = get_admin_password()
        return bool(admin_email and admin_password) and email == admin_email and password == admin_password

    def is_admin_authenticated():
        admin_email = get_admin_email()
        return bool(admin_email) and session.get("is_admin") is True and session.get("admin_email") == admin_email

    def grant_admin_session():
        admin_email = get_admin_email()
        if current_user.is_authenticated and current_user.is_admin and admin_email:
            session["is_admin"] = True
            session["admin_email"] = admin_email
            return True
        return False

    def get_admin_csrf_token():
        token = session.get("admin_csrf_token")
        if not token:
            token = secrets.token_hex(16)
            session["admin_csrf_token"] = token
        return token

    def validate_admin_csrf():
        submitted_token = request.form.get("csrf_token", "")
        return bool(submitted_token) and compare_digest(submitted_token, session.get("admin_csrf_token", ""))

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not get_admin_email():
                flash("Admin access is not configured.", "error")
                return redirect(url_for("login"))
            if not current_user.is_authenticated:
                return redirect(url_for("login", next=request.path))
            if not current_user.is_admin:
                flash("You do not have permission to access the admin panel.", "error")
                return redirect(url_for("dashboard"))
            if not is_admin_authenticated():
                grant_admin_session()
            return view(*args, **kwargs)

        return wrapped

    @app.context_processor
    def inject_admin_context():
        return {
            "admin_session_active": is_admin_authenticated(),
            "admin_csrf_token": get_admin_csrf_token() if is_admin_authenticated() else "",
        }

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        return redirect(url_for("login", next=request.args.get("next")))

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        session.pop("admin_email", None)
        session.pop("admin_csrf_token", None)
        flash("Admin access closed.", "info")
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        users = User.query.order_by(User.created_at.desc(), User.id.desc()).all()
        usage_sessions = UserAppSession.query.order_by(UserAppSession.last_active_at.desc(), UserAppSession.id.desc()).all()
        quiz_history = QuizHistory.query.order_by(QuizHistory.created_at.desc(), QuizHistory.id.desc()).all()
        word_rows = UserWord.query.all()

        now = datetime.utcnow()
        recent_threshold = now - timedelta(days=7)

        words_by_user = {}
        for row in word_rows:
            words_by_user[row.user_id] = words_by_user.get(row.user_id, 0) + 1

        quizzes_by_user = {}
        for row in quiz_history:
            quizzes_by_user[row.user_id] = quizzes_by_user.get(row.user_id, 0) + 1

        usage_by_user = {}
        for row in usage_sessions:
            bucket = usage_by_user.setdefault(
                row.user_id,
                {
                    "visits": 0,
                    "active_seconds": 0,
                    "page_views": 0,
                    "interactions": 0,
                    "last_seen_at": None,
                },
            )
            bucket["visits"] += 1
            bucket["active_seconds"] += row.active_seconds or 0
            bucket["page_views"] += row.page_views or 0
            bucket["interactions"] += row.interaction_count or 0
            if row.last_active_at and (bucket["last_seen_at"] is None or row.last_active_at > bucket["last_seen_at"]):
                bucket["last_seen_at"] = row.last_active_at

        user_rows = []
        for user in users:
            usage = usage_by_user.get(user.id, {})
            user_rows.append(
                {
                    "user": user,
                    "word_count": words_by_user.get(user.id, 0),
                    "quiz_count": quizzes_by_user.get(user.id, 0),
                    "visit_count": usage.get("visits", 0),
                    "active_minutes": round((usage.get("active_seconds", 0) or 0) / 60),
                    "page_views": usage.get("page_views", 0),
                    "interactions": usage.get("interactions", 0),
                    "last_seen_at": usage.get("last_seen_at"),
                }
            )

        summary = {
            "total_users": len(users),
            "restricted_users": sum(1 for user in users if user.is_restricted),
            "active_users_7d": len({row.user_id for row in usage_sessions if row.last_active_at and row.last_active_at >= recent_threshold}),
            "total_words": len(word_rows),
            "total_quizzes": len(quiz_history),
            "total_visits": len(usage_sessions),
            "total_active_hours": round(sum((row.active_seconds or 0) for row in usage_sessions) / 3600, 1),
        }

        return render_template(
            "admin_dashboard.html",
            admin_email=get_admin_email(),
            admin_summary=summary,
            user_rows=user_rows,
        )

    @app.route("/admin/users/<int:user_id>/restriction", methods=["POST"])
    @admin_required
    def admin_update_user_restriction(user_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        user = User.query.get_or_404(user_id)
        action = request.form.get("action", "").strip().lower()
        reason = request.form.get("restricted_reason", "").strip()

        if user.email.strip().lower() == get_admin_email():
            flash("The reserved admin email cannot be modified from the user controls.", "error")
            return redirect(url_for("admin_dashboard"))

        if action == "restrict":
            user.is_restricted = True
            user.restricted_reason = reason[:500] if reason else "Restricted by the administrator."
            flash(f"{user.email} has been restricted.", "success")
        elif action == "unrestrict":
            user.is_restricted = False
            user.restricted_reason = None
            flash(f"{user.email} has been restored.", "success")
        else:
            flash("Invalid admin action.", "error")
            return redirect(url_for("admin_dashboard"))

        db.session.commit()
        return redirect(url_for("admin_dashboard"))
