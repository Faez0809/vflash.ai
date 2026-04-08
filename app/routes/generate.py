from datetime import date

from flask import flash, redirect, request, session, url_for
from flask_login import current_user, login_required

from app.models import StudySession, UserWord, Word, db
from app.services.learning_content import (
    FALLBACK_CONTINUE_MESSAGE,
    ensure_starter_pack_for_user,
    find_cached_study_session,
    upsert_word_from_payload,
)
from app.services.ai_generator import generate_vocabulary_words
from app.services.stats import VOCAB_QUERY_MESSAGE, clean_text, pluralize, validate_vocabulary_query


def register(app):
    @app.route("/generate-words", methods=["POST"])
    @login_required
    def generate_words():
        difficulty = request.form.get("difficulty", "Beginner").strip().title()
        difficulty_map = {
            "Beginner": "Beginner",
            "Medium": "Intermediate",
            "Intermediate": "Intermediate",
            "Hard": "Advanced",
            "Advanced": "Advanced",
        }
        difficulty = difficulty_map.get(difficulty, "Beginner")

        try:
            word_count = int(request.form.get("word_count", "5"))
        except ValueError:
            word_count = 5

        if word_count not in {5, 10, 15}:
            word_count = 5

        custom_prompt = clean_text(request.form.get("custom_prompt"))
        if custom_prompt:
            prompt_state = validate_vocabulary_query(custom_prompt)
            if not prompt_state["valid"]:
                flash(prompt_state["message"] or VOCAB_QUERY_MESSAGE, "error")
                return redirect(f"{url_for('dashboard')}#generate-section")
            custom_prompt = prompt_state["normalized"]

        save_as_default = request.form.get("save_as_default") == "on"
        default_study_focus = clean_text(current_user.default_study_focus)
        last_search_topic = clean_text(session.get("last_search_topic"))
        effective_prompt = custom_prompt or default_study_focus or last_search_topic or ""

        if save_as_default:
            current_user.default_study_focus = custom_prompt or None

        if not default_study_focus and last_search_topic and not custom_prompt:
            flash("Tip: Set a default topic for consistent results.", "info")

        cached_session = find_cached_study_session(
            current_user.id,
            difficulty,
            word_count,
            effective_prompt,
        )
        if cached_session:
            if save_as_default:
                db.session.commit()
            flash("Loaded a matching study set from your saved collection.", "info")
            return redirect(url_for("flashcards_session", session_id=cached_session.id))

        learned_user_words = {
            row[0]
            for row in (
                db.session.query(Word.word)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(
                    UserWord.user_id == current_user.id,
                    UserWord.learned.is_(True),
                )
                .all()
            )
        }
        existing_user_words = {
            row[0]
            for row in (
                db.session.query(Word.word)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(UserWord.user_id == current_user.id)
                .all()
            )
        }
        generated_words = []
        seen_words = set(existing_user_words)
        attempts = 0
        max_attempts = max(6, word_count * 3)

        while len(generated_words) < word_count and attempts < max_attempts:
            attempts += 1
            remaining = word_count - len(generated_words)
            ai_words = generate_vocabulary_words(
                difficulty=difficulty,
                word_count=remaining,
                user_custom_prompt=effective_prompt,
                avoid_words=sorted(learned_user_words),
            )

            for item in ai_words:
                normalized_word = clean_text(item.get("word")).lower()
                already_exists_for_user = (
                    db.session.query(UserWord.id)
                    .join(Word, UserWord.word_id == Word.id)
                    .filter(
                        UserWord.user_id == current_user.id,
                        Word.word == normalized_word,
                    )
                    .first()
                    is not None
                )
                if not normalized_word or normalized_word in seen_words or already_exists_for_user:
                    continue

                item["word"] = normalized_word
                generated_words.append(item)
                seen_words.add(normalized_word)

                if len(generated_words) >= word_count:
                    break

        if not generated_words:
            starter_pack = ensure_starter_pack_for_user(current_user.id, effective_prompt)
            if save_as_default:
                db.session.commit()

            if starter_pack["created"] and starter_pack["session_id"]:
                flash(
                    "Fresh AI content is still being prepared. We've opened a starter vocabulary set so you can begin immediately.",
                    "info",
                )
                return redirect(url_for("flashcards_session", session_id=starter_pack["session_id"]))

            flash(FALLBACK_CONTINUE_MESSAGE, "info")
            return redirect(url_for("flashcards"))

        study_session = StudySession(
            user_id=current_user.id,
            difficulty=difficulty,
            word_count=len(generated_words),
            custom_prompt=effective_prompt or None,
            created_at=date.today(),
        )
        db.session.add(study_session)
        db.session.flush()
        added_count = 0

        for item in generated_words:
            normalized_word = clean_text(item.get("word")).lower()
            if not normalized_word:
                continue

            topic = clean_text(item.get("topic")) or (effective_prompt[:120] if effective_prompt else "General")
            item["topic"] = topic
            item["difficulty"] = clean_text(item.get("difficulty")) or difficulty
            word = upsert_word_from_payload(
                item,
                fallback_topic=topic or "General",
                fallback_difficulty=difficulty,
            )
            if word is None:
                continue

            existing_user_word = UserWord.query.filter_by(
                user_id=current_user.id,
                word_id=word.id,
            ).first()
            if existing_user_word:
                continue

            db.session.add(
                UserWord(
                    user_id=current_user.id,
                    word_id=word.id,
                    session_id=study_session.id,
                    added_date=date.today(),
                    learned=False,
                )
            )
            added_count += 1

        db.session.commit()
        if save_as_default:
            flash("Your default study focus has been updated.", "info")
        if added_count == word_count:
            flash(f"{pluralize(added_count, 'new word')} generated for your study list.", "success")
        elif added_count:
            flash(
                f"{pluralize(added_count, 'new word')} generated. The AI repeated too many existing words before reaching {pluralize(word_count, 'word')}.",
                "info",
            )
        else:
            flash("No new words were added because they already exist in your study list.", "info")
        return redirect(url_for("flashcards_session", session_id=study_session.id))
