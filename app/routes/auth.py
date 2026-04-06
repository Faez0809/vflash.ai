from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db


def register(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("Welcome back.", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))

            flash("Invalid email or password.", "error")

        return render_template("login.html")

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
                flash("Account created successfully. Please log in.", "success")
                return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))
