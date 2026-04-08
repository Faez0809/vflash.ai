from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db
from app.services.learning_content import ensure_starter_pack_for_user


def register(app):
    def matches_admin_credentials(email, password):
        admin_email = (current_app.config.get("ADMIN_EMAIL") or "").strip().lower()
        admin_password = current_app.config.get("ADMIN_PASSWORD") or ""
        return bool(admin_email and admin_password) and email == admin_email and password == admin_password

    def clear_password_reset_state():
        session.pop("password_reset_email", None)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        clear_password_reset_state()
        login_error = None
        show_forgot_password = False
        email_value = ""

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            email_value = email

            user = User.query.filter_by(email=email).first()
            if user and user.is_restricted:
                login_error = user.restricted_reason or "Your account has been restricted."
            elif user and check_password_hash(user.password, password):
                user.last_login_at = datetime.utcnow()
                db.session.commit()
                login_user(user)
                clear_password_reset_state()
                if matches_admin_credentials(email, password):
                    session["is_admin"] = True
                    session["admin_email"] = email
                    flash("Admin access is available from your dashboard.", "success")
                else:
                    session.pop("is_admin", None)
                    session.pop("admin_email", None)
                    session.pop("admin_csrf_token", None)
                flash("Signed in successfully.", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            elif user:
                login_error = "Incorrect password."
                show_forgot_password = True
            else:
                login_error = "Invalid email or password."

        return render_template(
            "login.html",
            login_error=login_error,
            show_forgot_password=show_forgot_password,
            email_value=email_value,
        )

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        support_email = (current_app.config.get("ADMIN_EMAIL") or "faezmahmud376@gmail.com").strip() or "faezmahmud376@gmail.com"
        recovery_error = None
        recovery_notice = None
        verification_failed = False
        verified_email = session.get("password_reset_email")
        email_value = verified_email or request.args.get("email", "").strip().lower()
        nickname_value = ""

        if request.method == "POST":
            step = request.form.get("step", "verify").strip().lower()

            if step == "verify":
                clear_password_reset_state()
                email_value = request.form.get("email", "").strip().lower()
                nickname_value = request.form.get("nickname", "").strip()
                user = User.query.filter_by(email=email_value).first()

                if not user:
                    recovery_error = "No account was found for that email address."
                elif user.nickname.strip().lower() != nickname_value.lower():
                    verification_failed = True
                    recovery_error = f"Nickname did not match. Contact support at {support_email}."
                else:
                    session["password_reset_email"] = user.email.strip().lower()
                    verified_email = user.email.strip().lower()
                    recovery_notice = "Nickname verified. Set a new password."
            else:
                verified_email = session.get("password_reset_email")
                password = request.form.get("password", "")
                confirm_password = request.form.get("confirm_password", "")

                if not verified_email:
                    return redirect(url_for("forgot_password"))

                user = User.query.filter_by(email=verified_email).first()
                if not user:
                    clear_password_reset_state()
                    recovery_error = "This recovery session is no longer valid. Try again."
                    verified_email = None
                elif len(password) < 8:
                    recovery_error = "Your new password must be at least 8 characters long."
                elif password != confirm_password:
                    recovery_error = "The new passwords do not match."
                else:
                    user.password = generate_password_hash(password)
                    db.session.commit()
                    clear_password_reset_state()
                    flash("Your password has been updated. You can sign in now.", "success")
                    return redirect(url_for("login"))

        return render_template(
            "forgot_password.html",
            support_email=support_email,
            recovery_error=recovery_error,
            recovery_notice=recovery_notice,
            verification_failed=verification_failed,
            verified_email=verified_email,
            email_value=email_value,
            nickname_value=nickname_value,
        )

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            nickname = request.form.get("nickname", "").strip()

            if not email or not password or not nickname:
                flash("Email, nickname, and password are required.", "error")
            elif password != confirm_password:
                flash("Passwords do not match.", "error")
            elif len(nickname) < 2:
                flash("Nickname must be at least 2 characters.", "error")
            elif User.query.filter_by(email=email).first():
                flash("An account with that email already exists.", "error")
            else:
                user = User(
                    email=email,
                    password=generate_password_hash(password),
                    nickname=nickname[:80],
                )
                db.session.add(user)
                db.session.commit()
                starter_pack = ensure_starter_pack_for_user(user.id)
                if starter_pack["created"]:
                    flash("Account created successfully. Starter vocabulary is ready for you.", "success")
                else:
                    flash("Account created successfully. Please log in.", "success")
                return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.pop("is_admin", None)
        session.pop("admin_email", None)
        session.pop("admin_csrf_token", None)
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))
