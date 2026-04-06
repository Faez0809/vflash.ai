from datetime import date

from flask import flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.models import StudySession, UserWord, Word, db
from app.services.ai_generator import generate_vocabulary_words
from app.services.stats import clean_text, pluralize


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

        custom_prompt = request.form.get("custom_prompt", "").strip()
        save_as_default = request.form.get("save_as_default") == "on"
        effective_prompt = custom_prompt or clean_text(current_user.default_study_focus)

        if save_as_default:
            current_user.default_study_focus = custom_prompt or None

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
            if save_as_default:
                db.session.commit()
            flash("Could not generate new words right now. Please try again.", "error")
            return redirect(url_for("dashboard"))

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

            word = Word.query.filter_by(word=normalized_word).first()
            part_of_speech = clean_text(item.get("part_of_speech"))
            meaning = clean_text(item.get("meaning"))
            bangla_meaning = clean_text(item.get("bangla_meaning"))
            phonetic = clean_text(item.get("phonetic"))
            synonym = clean_text(item.get("synonym"))
            memory_trick = clean_text(item.get("memory_trick"))
            item_difficulty = clean_text(item.get("difficulty")) or difficulty
            topic = clean_text(item.get("topic")) or (effective_prompt[:120] if effective_prompt else "General")
            sentence = clean_text(item.get("sentence"))

            if word is None:
                word = Word(
                    word=normalized_word,
                    part_of_speech=part_of_speech or None,
                    meaning=meaning,
                    bangla_meaning=bangla_meaning or None,
                    phonetic=phonetic or None,
                    synonym=synonym or None,
                    memory_trick=memory_trick or None,
                    difficulty=item_difficulty,
                    topic=topic or None,
                    sentence=sentence,
                    created_at=date.today(),
                )
                db.session.add(word)
                db.session.flush()
            else:
                if not word.part_of_speech and part_of_speech:
                    word.part_of_speech = part_of_speech
                if not word.meaning and meaning:
                    word.meaning = meaning
                if not word.bangla_meaning and bangla_meaning:
                    word.bangla_meaning = bangla_meaning
                if not word.phonetic and phonetic:
                    word.phonetic = phonetic
                if not word.synonym and synonym:
                    word.synonym = synonym
                if not word.memory_trick and memory_trick:
                    word.memory_trick = memory_trick
                if not word.difficulty:
                    word.difficulty = difficulty
                if not word.topic and topic:
                    word.topic = topic
                if not word.sentence and sentence:
                    word.sentence = sentence
                if not word.created_at:
                    word.created_at = date.today()

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
