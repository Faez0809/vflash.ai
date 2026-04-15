from datetime import date
import random

from flask import flash, redirect, request, session, url_for
from flask_login import current_user, login_required

from app.models import StudySession, UserWord, Word, db
from app.services.learning_content import invalidate_word_list_cache, upsert_word_from_payload
from app.services.ai_generator import generate_vocabulary_words
from app.services.stats import VOCAB_QUERY_MESSAGE, clean_text, pluralize, validate_vocabulary_query


def register(app):
    general_exhausted_message = "We could not generate enough new valid words right now. Please try again."
    max_generation_attempts = 8
    default_topic_messages = [
        "Tip: Add a topic (e.g., business, travel) to explore more diverse vocabulary.",
        "Want more variety? Try entering a custom topic.",
        "You're learning IELTS vocabulary. Add a topic to focus your learning.",
        "Explore more words by choosing a specific topic.",
        "Tip: Custom topics can make learning more interesting.",
    ]

    def normalize_generated_payload(item, fallback_topic, fallback_difficulty):
        return {
            "word": clean_text((item or {}).get("word")).lower(),
            "part_of_speech": clean_text((item or {}).get("part_of_speech")) or None,
            "meaning": clean_text((item or {}).get("meaning")) or None,
            "bangla_meaning": clean_text((item or {}).get("bangla_meaning")) or None,
            "bangla_pronunciation": clean_text((item or {}).get("bangla_pronunciation")) or None,
            "phonetic": clean_text((item or {}).get("phonetic")) or None,
            "synonym": clean_text((item or {}).get("synonym")) or None,
            "memory_trick": clean_text((item or {}).get("memory_trick")) or None,
            "sentence": clean_text((item or {}).get("sentence")) or None,
            "topic": clean_text((item or {}).get("topic")) or fallback_topic,
            "difficulty": clean_text((item or {}).get("difficulty")) or fallback_difficulty,
        }

    def get_excluded_words_for_user(user_id, topic_hint="", recent_limit=100):
        recent_rows = (
            db.session.query(Word.word)
            .join(UserWord, UserWord.word_id == Word.id)
            .filter(UserWord.user_id == user_id)
            .order_by(UserWord.added_date.desc(), UserWord.id.desc())
            .limit(recent_limit)
            .all()
        )
        excluded_words = {
            clean_text(row[0]).lower()
            for row in recent_rows
            if clean_text(row[0])
        }

        latest_session = (
            StudySession.query.filter_by(user_id=user_id, custom_prompt=topic_hint or None)
            .order_by(StudySession.id.desc())
            .first()
        )
        if latest_session is not None:
            last_session_rows = (
                db.session.query(Word.word)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(UserWord.user_id == user_id, UserWord.session_id == latest_session.id)
                .all()
            )
            excluded_words.update(
                clean_text(row[0]).lower()
                for row in last_session_rows
                if clean_text(row[0])
            )

        return excluded_words

    @app.route("/generate-words", methods=["POST"])
    @login_required
    def generate_words():
        try:
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
            topic_seed = (custom_prompt or default_study_focus or last_search_topic or "").strip()
            is_default_topic = not bool(topic_seed)
            if topic_seed:
                effective_prompt = f"{topic_seed} with IELTS-level vocabulary"
            else:
                effective_prompt = "IELTS standard English vocabulary"
            soft_message = random.choice(default_topic_messages) if is_default_topic else None
            print("Topic:", effective_prompt)

            if save_as_default:
                current_user.default_study_focus = custom_prompt or None

            excluded_words = get_excluded_words_for_user(current_user.id, topic_hint=effective_prompt)
            session_words = set()
            final_words = []
            attempts = 0
            print("Requested:", word_count)

            while len(final_words) < word_count and attempts < max_generation_attempts:
                attempts += 1
                remaining = word_count - len(final_words)
                request_count = min(10, remaining * 2)
                ai_words = generate_vocabulary_words(
                    difficulty=difficulty,
                    word_count=request_count,
                    user_custom_prompt=effective_prompt,
                    avoid_words=sorted(excluded_words.union(session_words)),
                )

                for item in ai_words:
                    normalized_item = normalize_generated_payload(
                        item,
                        fallback_topic=effective_prompt,
                        fallback_difficulty=difficulty,
                    )
                    normalized_word = normalized_item["word"]
                    if not normalized_word or normalized_word in session_words:
                        continue

                    final_words.append(normalized_item)
                    session_words.add(normalized_word)

                    if len(final_words) >= word_count:
                        break

            print("Final words:", len(final_words))
            print("Attempts:", attempts)
            print("Generated:", len(final_words))
            print("Generated count:", len(final_words))

            if len(final_words) == 0:
                fallback_words = generate_vocabulary_words(
                    difficulty=difficulty,
                    word_count=min(10, word_count),
                    user_custom_prompt="Generate common useful English vocabulary words",
                    avoid_words=sorted(excluded_words),
                )
                for item in fallback_words:
                    normalized_item = normalize_generated_payload(
                        item,
                        fallback_topic="IELTS standard English vocabulary",
                        fallback_difficulty=difficulty,
                    )
                    normalized_word = normalized_item["word"]
                    if not normalized_word or normalized_word in session_words:
                        continue
                    final_words.append(normalized_item)
                    session_words.add(normalized_word)
                    if len(final_words) >= word_count:
                        break

            if len(final_words) == 0:
                if save_as_default:
                    db.session.commit()
                flash(general_exhausted_message, "info")
                return redirect(url_for("flashcards"))

            study_session = StudySession(
                user_id=current_user.id,
                difficulty=difficulty,
                word_count=len(final_words),
                custom_prompt=effective_prompt or None,
                created_at=date.today(),
            )
            db.session.add(study_session)
            db.session.flush()
            added_count = 0
            candidate_words = {
                clean_text(item.get("word")).lower()
                for item in final_words
                if clean_text(item.get("word"))
            }
            existing_linked_words = {
                clean_text(row[0]).lower()
                for row in (
                    db.session.query(Word.word)
                    .join(UserWord, UserWord.word_id == Word.id)
                    .filter(UserWord.user_id == current_user.id, Word.word.in_(candidate_words))
                    .all()
                )
                if clean_text(row[0])
            }
            saved_words = set()

            for item in final_words:
                normalized_word = clean_text(item.get("word")).lower()
                if not normalized_word or normalized_word in saved_words:
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

                if normalized_word in existing_linked_words:
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
                existing_linked_words.add(normalized_word)
                saved_words.add(normalized_word)
                added_count += 1

            if added_count == 0:
                db.session.rollback()
                if save_as_default:
                    db.session.add(current_user)
                    db.session.commit()
                flash(general_exhausted_message, "info")
                return redirect(url_for("flashcards"))

            study_session.word_count = added_count
            db.session.commit()
            invalidate_word_list_cache()  # Keep global search suggestions fresh after inserts.
            if soft_message:
                flash(soft_message, "info")
            if save_as_default:
                flash("Your default study focus has been updated.", "info")
            if added_count < word_count:
                flash("Showing best available words for this topic.", "info")
            flash(f"{pluralize(added_count, 'new word')} generated for your study list.", "success")
            return redirect(url_for("flashcards_session", session_id=study_session.id))
        except Exception:
            db.session.rollback()
            flash(general_exhausted_message, "error")
            return redirect(url_for("flashcards"))
