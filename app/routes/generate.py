from datetime import date

from flask import flash, redirect, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_

from app.models import StudySession, UserWord, Word, db
from app.services.learning_content import (
    ensure_starter_pack_for_user,
    invalidate_word_list_cache,
    upsert_word_from_payload,
)
from app.services.ai_generator import generate_vocabulary_words
from app.services.stats import VOCAB_QUERY_MESSAGE, clean_text, pluralize, validate_vocabulary_query
from app.services.word_validation import validate_word_payload


def register(app):
    exhausted_topic_message = "We’ve covered all meaningful words for this topic. Try a broader or different topic."

    def difficulty_fallback_sequence(difficulty):
        order = ["Beginner", "Intermediate", "Advanced"]
        index_map = {label: position for position, label in enumerate(order)}
        start_index = index_map.get(difficulty, 0)
        return list(reversed(order[: start_index + 1]))

    def serialize_word_payload(word, fallback_topic, fallback_difficulty):
        return {
            "word": clean_text(getattr(word, "word", "")).lower(),
            "part_of_speech": clean_text(getattr(word, "part_of_speech", "")) or None,
            "meaning": clean_text(getattr(word, "meaning", "")) or None,
            "bangla_meaning": clean_text(getattr(word, "bangla_meaning", "")) or None,
            "bangla_pronunciation": clean_text(getattr(word, "bangla_pronunciation", "")) or None,
            "phonetic": clean_text(getattr(word, "phonetic", "")) or None,
            "synonym": clean_text(getattr(word, "synonym", "")) or None,
            "memory_trick": clean_text(getattr(word, "memory_trick", "")) or None,
            "sentence": clean_text(getattr(word, "sentence", "")) or None,
            "topic": clean_text(getattr(word, "topic", "")) or fallback_topic,
            "difficulty": clean_text(getattr(word, "difficulty", "")) or fallback_difficulty,
        }

    def fetch_reusable_words_for_user(user_id, difficulty, topic_hint, seen_words, limit):
        if limit <= 0:
            return []

        normalized_topic = clean_text(topic_hint)
        collected = []

        def collect(query):
            for word in query.limit(max(limit * 3, 20)).all():
                normalized_word = clean_text(getattr(word, "word", "")).lower()
                if not normalized_word or normalized_word in seen_words:
                    continue
                serialized = serialize_word_payload(
                    word,
                    fallback_topic=normalized_topic or "General",
                    fallback_difficulty=difficulty or "Beginner",
                )
                validation = validate_word_payload(
                    normalized_word,
                    payload=serialized,
                    topic_hint=normalized_topic,
                )
                if not validation["is_valid"]:
                    continue
                collected.append(serialized)
                seen_words.add(normalized_word)
                if len(collected) >= limit:
                    break

        for difficulty_candidate in difficulty_fallback_sequence(difficulty or "Beginner"):
            difficulty_query = (
                Word.query.outerjoin(
                    UserWord,
                    and_(UserWord.word_id == Word.id, UserWord.user_id == user_id),
                )
                .filter(UserWord.id.is_(None))
                .filter(Word.word.isnot(None), Word.is_valid.is_(True))
                .filter(Word.difficulty == difficulty_candidate)
            )

            if normalized_topic:
                collect(
                    difficulty_query.filter(Word.topic.isnot(None))
                    .filter(Word.topic.ilike(f"%{normalized_topic}%"))
                    .order_by(Word.created_at.desc().nullslast(), Word.id.desc())
                )
                if len(collected) >= limit:
                    return collected

            collect(difficulty_query.order_by(Word.created_at.desc().nullslast(), Word.id.desc()))
            if len(collected) >= limit:
                return collected
        return collected

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

        existing_user_words = {
            clean_text(row[0]).lower()
            for row in (
                db.session.query(Word.word)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(Word.is_valid.is_(True))
                .filter(UserWord.user_id == current_user.id)
                .all()
            )
            if clean_text(row[0])
        }
        generated_words = fetch_reusable_words_for_user(
            current_user.id,
            difficulty,
            effective_prompt,
            set(existing_user_words),
            word_count,
        )
        seen_words = {clean_text(item.get("word")).lower() for item in generated_words if clean_text(item.get("word"))}
        seen_words.update(existing_user_words)
        attempts = 0
        max_attempts = max(2, min(4, word_count))

        requested_sequence = difficulty_fallback_sequence(difficulty)
        used_lower_level_fallback = False

        while len(generated_words) < word_count and attempts < max_attempts:
            attempts += 1
            remaining = word_count - len(generated_words)
            for difficulty_candidate in requested_sequence:
                ai_words = generate_vocabulary_words(
                    difficulty=difficulty_candidate,
                    word_count=remaining,
                    user_custom_prompt=effective_prompt,
                    avoid_words=sorted(seen_words),
                )

                for item in ai_words:
                    normalized_word = clean_text(item.get("word")).lower()
                    if not normalized_word or normalized_word in seen_words:
                        continue
                    validation = validate_word_payload(
                        normalized_word,
                        payload=item,
                        topic_hint=effective_prompt,
                    )
                    if not validation["is_valid"]:
                        continue

                    item["word"] = normalized_word
                    generated_words.append(item)
                    seen_words.add(normalized_word)
                    if difficulty_candidate != difficulty:
                        used_lower_level_fallback = True

                    if len(generated_words) >= word_count:
                        break

                remaining = word_count - len(generated_words)
                if remaining <= 0:
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

            flash(exhausted_topic_message, "info")
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
        existing_word_links = {
            row[0]
            for row in db.session.query(UserWord.word_id).filter(UserWord.user_id == current_user.id).all()
        }

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

            if word.id in existing_word_links:
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
            existing_word_links.add(word.id)
            added_count += 1

        db.session.commit()
        if added_count:
            invalidate_word_list_cache()  # Keep global search suggestions fresh after inserts.
        if save_as_default:
            flash("Your default study focus has been updated.", "info")
        if added_count == word_count:
            if used_lower_level_fallback:
                flash(
                    f"{pluralize(added_count, 'new word')} generated for your study list. Lower-level words were included to keep the topic set complete.",
                    "success",
                )
            else:
                flash(f"{pluralize(added_count, 'new word')} generated for your study list.", "success")
        elif added_count:
            flash(f"{pluralize(added_count, 'new word')} generated for your study list.", "success")
            flash(exhausted_topic_message, "info")
        else:
            flash(exhausted_topic_message, "info")
        return redirect(url_for("flashcards_session", session_id=study_session.id))
