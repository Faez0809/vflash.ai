import secrets
from datetime import date, datetime, timedelta
from functools import wraps
from hmac import compare_digest

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user
from app.db_health import default_database_health, get_database_health
from app.models import (
    FlashcardSessionWord,
    QuizHistory,
    SearchHistory,
    User,
    UserAppSession,
    UserWordProgress,
    VocabularyEnrichment,
    VocabularyMaster,
    VocabularyReviewFlag,
    db,
)
from app.services.stats import clean_text
from app.services.vocabulary_platform import (
    apply_enrichment_audit,
    apply_vocabulary_correction,
    normalize_level,
    normalize_vocab_text,
    regenerate_vocabulary_enrichment,
)
from scripts.reset_legacy_progress import reset_learning_journey


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
        db_health = default_database_health()
        enrichment_page = max(1, request.args.get("enrichment_page", 1, type=int))
        flag_page = max(1, request.args.get("flag_page", 1, type=int))
        user_page = max(1, request.args.get("user_page", 1, type=int))
        enrichment_q = clean_text(request.args.get("enrichment_q"))
        level_filter = clean_text(request.args.get("level_filter"))
        quality_filter = clean_text(request.args.get("quality_filter"))
        flag_status = clean_text(request.args.get("flag_status")) or "pending"
        flag_type = clean_text(request.args.get("flag_type"))
        user_total = User.query.count()
        users = (
            User.query.order_by(User.created_at.desc(), User.id.desc())
            .offset((user_page - 1) * 25)
            .limit(25)
            .all()
        )
        usage_sessions = UserAppSession.query.order_by(UserAppSession.last_active_at.desc(), UserAppSession.id.desc()).all()
        quiz_history = QuizHistory.query.order_by(QuizHistory.created_at.desc(), QuizHistory.id.desc()).all()
        word_rows = UserWordProgress.query.all()
        enrichment_query = (
            VocabularyEnrichment.query.join(VocabularyMaster)
        )
        if enrichment_q:
            search_term = f"%{enrichment_q}%"
            enrichment_query = enrichment_query.filter(VocabularyMaster.word.ilike(search_term))
        if level_filter:
            enrichment_query = enrichment_query.filter(VocabularyMaster.level == normalize_level(level_filter))
        if quality_filter == "flagged":
            enrichment_query = enrichment_query.filter(VocabularyMaster.needs_admin_review.is_(True))
        elif quality_filter == "low_quality":
            enrichment_query = enrichment_query.filter(VocabularyEnrichment.enrichment_quality_score < 80)
        elif quality_filter == "never_audited":
            enrichment_query = enrichment_query.filter(VocabularyEnrichment.last_audited_at.is_(None))
        elif quality_filter == "recently_audited":
            enrichment_query = enrichment_query.filter(VocabularyEnrichment.last_audited_at.isnot(None))
        elif quality_filter == "corrected":
            enrichment_query = enrichment_query.filter(VocabularyMaster.corrected_at.isnot(None))
        elif quality_filter == "regenerated":
            enrichment_query = enrichment_query.filter(VocabularyEnrichment.last_regenerated_at.isnot(None))
        enrichment_total = enrichment_query.count()
        enrichment_rows = (
            enrichment_query.order_by(
                    VocabularyEnrichment.quality_verified.asc(),
                    VocabularyEnrichment.enrichment_quality_score.asc(),
                    VocabularyMaster.level.asc(),
                    VocabularyMaster.word.asc(),
                )
                .offset((enrichment_page - 1) * 15)
                .limit(15)
                .all()
        )
        review_flag_query = VocabularyReviewFlag.query.outerjoin(VocabularyMaster)
        if flag_status != "all":
            review_flag_query = review_flag_query.filter(VocabularyReviewFlag.status == flag_status)
        if flag_type:
            review_flag_query = review_flag_query.filter(VocabularyReviewFlag.flag_type == flag_type)
        review_flag_total = review_flag_query.count()
        review_flags = (
            review_flag_query.order_by(VocabularyReviewFlag.created_at.desc(), VocabularyReviewFlag.id.desc())
            .offset((flag_page - 1) * 15)
            .limit(15)
            .all()
        )

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
            "total_users": user_total,
            "restricted_users": User.query.filter_by(is_restricted=True).count(),
            "active_users_7d": len({row.user_id for row in usage_sessions if row.last_active_at and row.last_active_at >= recent_threshold}),
            "total_words": len(word_rows),
            "total_quizzes": len(quiz_history),
            "total_visits": len(usage_sessions),
            "total_active_hours": round(sum((row.active_seconds or 0) for row in usage_sessions) / 3600, 1),
            "flagged_enrichments": VocabularyEnrichment.query.filter(
                (VocabularyEnrichment.quality_verified.is_(False))
                | (VocabularyEnrichment.enrichment_quality_score < 80)
                | (VocabularyEnrichment.audit_flags.isnot(None))
            ).count(),
            "review_flags": VocabularyReviewFlag.query.filter_by(status="pending").count(),
        }
        try:
            db_health = get_database_health(current_app)
        except Exception as exc:
            current_app.logger.exception("Database health check failed")
            db_health["status"] = "error"
            db_health["healthy"] = False
            db_health["error"] = str(exc)
            db_health["connection_error"] = str(exc)

        return render_template(
            "admin_dashboard.html",
            admin_email=get_admin_email(),
            admin_summary=summary,
            db_health=db_health,
            user_rows=user_rows,
            enrichment_rows=enrichment_rows,
            enrichment_page=enrichment_page,
            enrichment_total=enrichment_total,
            enrichment_q=enrichment_q,
            review_flags=review_flags,
            review_flag_total=review_flag_total,
            flag_page=flag_page,
            flag_status=flag_status,
            flag_type=flag_type,
            level_filter=level_filter,
            quality_filter=quality_filter,
            user_page=user_page,
            user_total=user_total,
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
        return redirect(request.referrer or url_for("admin_dashboard"))

    @app.route("/admin/review-flags/<int:flag_id>/action", methods=["POST"])
    @admin_required
    def admin_review_flag_action(flag_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        flag = VocabularyReviewFlag.query.get_or_404(flag_id)
        action = clean_text(request.form.get("action")).lower()
        vocabulary = flag.vocabulary

        if action == "approve":
            flag.status = "approved"
            flag.resolved_at = datetime.utcnow()
            flash("Review flag approved.", "success")
        elif action == "edit" and vocabulary is not None:
            word = clean_text(request.form.get("word"))[:180]
            level = normalize_level(request.form.get("level"))
            if word:
                vocabulary.word = word
                vocabulary.normalized_word = normalize_vocab_text(word)
                vocabulary.is_phrase = " " in vocabulary.normalized_word
            if level:
                vocabulary.level = level
            flag.corrected_word = vocabulary.word
            flag.status = "edited"
            flag.resolved_at = datetime.utcnow()
            flash(f"Updated flagged word {vocabulary.word}.", "success")
        elif action == "reassign" and vocabulary is not None:
            level = normalize_level(request.form.get("level"))
            if level:
                vocabulary.level = level
                flag.level = level
            flag.status = "reassigned"
            flag.resolved_at = datetime.utcnow()
            flash(f"Reassigned {vocabulary.word}.", "success")
        elif action == "delete" and vocabulary is not None:
            word = vocabulary.word
            FlashcardSessionWord.query.filter_by(vocabulary_id=vocabulary.id).delete(synchronize_session=False)
            UserWordProgress.query.filter_by(vocabulary_id=vocabulary.id).delete(synchronize_session=False)
            SearchHistory.query.filter_by(matched_vocabulary_id=vocabulary.id).update({"matched_vocabulary_id": None}, synchronize_session=False)
            db.session.delete(vocabulary)
            flag.vocabulary_id = None
            flag.status = "deleted"
            flag.resolved_at = datetime.utcnow()
            flash(f"Deleted flagged vocabulary word '{word}'.", "success")
        else:
            flash("Invalid review action.", "error")
            return redirect(url_for("admin_dashboard"))

        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/users/<int:user_id>/reset-learning", methods=["POST"])
    @admin_required
    def admin_reset_learning_journey(user_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        user = User.query.get_or_404(user_id)
        reset_learning_journey(user.id)
        flash(f"{user.email}'s learning journey has been reset.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/enrichments/<int:enrichment_id>/edit", methods=["POST"])
    @admin_required
    def admin_edit_enrichment(enrichment_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        enrichment = VocabularyEnrichment.query.get_or_404(enrichment_id)
        vocabulary = enrichment.vocabulary
        word = clean_text(request.form.get("word"))[:180]
        if word:
            apply_vocabulary_correction(vocabulary, word, original_word=vocabulary.word, corrected_by_admin=True)
        vocabulary.level = normalize_level(request.form.get("level") or vocabulary.level)
        vocabulary.needs_admin_review = request.form.get("needs_admin_review") == "1"
        vocabulary.review_reason = clean_text(request.form.get("review_reason")) or None
        enrichment.definition = clean_text(request.form.get("definition")) or enrichment.definition
        enrichment.bangla_meaning = clean_text(request.form.get("bangla_meaning")) or None
        enrichment.pronunciation = clean_text(request.form.get("pronunciation")) or None
        enrichment.synonyms = clean_text(request.form.get("synonyms")) or None
        enrichment.antonyms = clean_text(request.form.get("antonyms")) or None
        enrichment.example_sentence = clean_text(request.form.get("example_sentence")) or None
        enrichment.memory_tip = None
        enrichment.corrected_manually = True
        apply_enrichment_audit(vocabulary, enrichment)
        db.session.commit()
        flash(f"Updated enrichment for {vocabulary.word}.", "success")
        return redirect(request.referrer or url_for("admin_dashboard"))

    @app.route(
        "/admin/enrichments/<int:enrichment_id>/regenerate",
        methods=["POST"],
        endpoint="admin_regenerate_enrichment",
    )
    @admin_required
    def admin_regenerate_enrichment(enrichment_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        enrichment = VocabularyEnrichment.query.get_or_404(enrichment_id)
        vocabulary = enrichment.vocabulary
        admin_prompt = clean_text(request.form.get("admin_prompt"))
        try:
            regenerate_vocabulary_enrichment(vocabulary, admin_prompt=admin_prompt)
            db.session.commit()
            flash(f"Regenerated enrichment for {vocabulary.word}.", "success")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Admin enrichment regeneration failed")
            flash("Could not regenerate this enrichment right now.", "error")
        return redirect(request.referrer or url_for("admin_dashboard"))

    @app.route("/admin/vocabulary/<int:vocabulary_id>/delete", methods=["POST"])
    @admin_required
    def admin_delete_vocabulary(vocabulary_id):
        if not validate_admin_csrf():
            flash("Security check failed. Please try again.", "error")
            return redirect(url_for("admin_dashboard"))

        vocabulary = VocabularyMaster.query.get_or_404(vocabulary_id)
        word = vocabulary.word
        try:
            FlashcardSessionWord.query.filter_by(vocabulary_id=vocabulary.id).delete(synchronize_session=False)
            UserWordProgress.query.filter_by(vocabulary_id=vocabulary.id).delete(synchronize_session=False)
            SearchHistory.query.filter_by(matched_vocabulary_id=vocabulary.id).update(
                {"matched_vocabulary_id": None},
                synchronize_session=False,
            )
            if vocabulary.enrichment is not None:
                db.session.delete(vocabulary.enrichment)
            db.session.delete(vocabulary)
            db.session.commit()
            flash(f"Deleted vocabulary word '{word}'.", "success")
        except Exception:
            db.session.rollback()
            flash("Could not delete that vocabulary word safely.", "error")
        return redirect(url_for("admin_dashboard"))
