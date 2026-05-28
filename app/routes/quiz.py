from datetime import date, datetime
import json

from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models import QuizHistory, UserWordProgress, db
from app.services.quiz_engine import (
    LEVEL_OPTIONS,
    QUESTION_COUNTS,
    QUIZ_TYPES,
    WORD_SOURCES,
    build_curriculum_quiz_questions,
    count_quizable_vocabularies,
    quiz_started_at,
)
from app.services.stats import clean_text


def register(app):
    def quiz_signature(quiz_type, word_source, difficulty, question_count, focus):
        return "::".join([quiz_type, word_source, difficulty, str(question_count), clean_text(focus)])

    def build_questions_with_fallback(total_questions, quiz_type, difficulty, word_source, focus="", specific_vocabulary_ids=None):
        if specific_vocabulary_ids:
            questions = build_curriculum_quiz_questions(
                current_user.id,
                total_questions=total_questions,
                quiz_type=quiz_type,
                level=difficulty,
                word_source=word_source,
                focus=focus,
                specific_vocabulary_ids=specific_vocabulary_ids,
            )
            return {"questions": questions, "word_source": word_source, "difficulty": difficulty, "used_fallback": False}

        sources = []
        for source in [word_source, "difficult_words", "generated_words", "learned_words", "mixed_curriculum", "unseen_vocabulary"]:
            if source not in sources:
                sources.append(source)
        levels = []
        for level in [difficulty, "Mixed"]:
            if level and level not in levels:
                levels.append(level)

        for source in sources:
            for level in levels:
                questions = build_curriculum_quiz_questions(
                    current_user.id,
                    total_questions=total_questions,
                    quiz_type=quiz_type,
                    level=level,
                    word_source=source,
                    focus=focus,
                )
                if questions:
                    return {
                        "questions": questions,
                        "word_source": source,
                        "difficulty": level,
                        "used_fallback": source != word_source or level != difficulty,
                    }
        return {"questions": [], "word_source": word_source, "difficulty": difficulty, "used_fallback": False}

    def append_quiz_batch(quiz_state, batch_size=3):
        remaining = max(0, quiz_state["target_count"] - len(quiz_state["questions"]))
        if not remaining:
            return 0
        resolution = build_questions_with_fallback(
            total_questions=min(batch_size, remaining),
            quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
            difficulty=quiz_state.get("difficulty", "Mixed"),
            word_source=quiz_state.get("word_source", "mixed_curriculum"),
            focus=quiz_state.get("focus", ""),
        )
        new_questions = [
            question
            for question in resolution["questions"]
            if question.get("vocabulary_id") not in set(quiz_state.get("used_vocabulary_ids", []))
        ]
        quiz_state["questions"].extend(new_questions)
        quiz_state["used_vocabulary_ids"] = quiz_state.get("used_vocabulary_ids", []) + [
            question["vocabulary_id"] for question in new_questions if question.get("vocabulary_id")
        ]
        return len(new_questions)

    def finalize_quiz_result(quiz_state, mark_quit=False):
        answered_count = len(quiz_state["answers"])
        configured_total_questions = quiz_state.get("target_count", len(quiz_state["questions"]))
        wrong_answers = [answer for answer in quiz_state["answers"] if not answer["is_correct"]]
        wrong_vocabulary_ids = sorted({
            answer.get("vocabulary_id")
            for answer in wrong_answers
            if answer.get("vocabulary_id")
        })
        for vocabulary_id in wrong_vocabulary_ids:
            progress = UserWordProgress.query.filter_by(user_id=current_user.id, vocabulary_id=vocabulary_id).first()
            if progress is not None:
                progress.is_difficult = True
                progress.times_reviewed = (progress.times_reviewed or 0) + 1
                progress.updated_at = datetime.utcnow()

        history = QuizHistory(
            user_id=current_user.id,
            quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
            score=quiz_state["score"],
            total_questions=answered_count or len(quiz_state["questions"]),
            answered_questions=answered_count,
            configured_total_questions=configured_total_questions,
            was_quit=mark_quit,
            mistakes_json=json.dumps(wrong_answers),
            weak_vocabulary_ids=",".join(str(item) for item in wrong_vocabulary_ids),
            completion_seconds=max(0, int(datetime.utcnow().timestamp()) - int(quiz_state.get("started_at", quiz_started_at()))),
            retry_of_quiz_id=quiz_state.get("retry_of_quiz_id"),
            created_at=date.today(),
        )
        db.session.add(history)
        db.session.commit()

        session["quiz_result"] = {
            "score": quiz_state["score"],
            "total_questions": answered_count or len(quiz_state["questions"]),
            "configured_total_questions": configured_total_questions,
            "answers": quiz_state["answers"],
            "quiz_type": quiz_state.get("quiz_type", "multiple_choice"),
            "difficulty": quiz_state.get("difficulty", "Mixed"),
            "word_source": quiz_state.get("word_source", "mixed_curriculum"),
            "focus": quiz_state.get("focus", ""),
            "accuracy": round((quiz_state["score"] / answered_count) * 100) if answered_count else 0,
            "correct_count": quiz_state["score"],
            "wrong_count": max(0, answered_count - quiz_state["score"]),
            "wrong_word_ids": wrong_vocabulary_ids,
            "was_quit": mark_quit,
            "history_id": history.id,
        }
        session.pop("quiz_state", None)

    @app.route("/quiz", methods=["GET"])
    @login_required
    def quiz():
        if request.args.get("reset") == "1":
            session.pop("quiz_state", None)
            session.pop("quiz_result", None)
            return redirect(url_for("quiz"))
        if request.args.get("result") == "1" and session.get("quiz_result"):
            return render_template("quiz.html", quiz_result=session.get("quiz_result"), quiz_setup=None)
        quiz_state = session.get("quiz_state")
        if quiz_state:
            return redirect(url_for("quiz_start"))

        session.pop("quiz_result", None)
        return render_template(
            "quiz.html",
            quiz_setup={
                "quiz_types": [*QUIZ_TYPES],
                "word_sources": [*WORD_SOURCES],
                "difficulty_options": [*LEVEL_OPTIONS],
                "question_counts": [*QUESTION_COUNTS],
                "has_resume": False,
                "resume_progress": None,
            },
            quiz_result=None,
        )

    @app.route("/quiz/start", methods=["GET", "POST"])
    @login_required
    def quiz_start():
        quiz_state = session.get("quiz_state")

        if request.args.get("retry") == "wrong":
            quiz_result = session.get("quiz_result") or {}
            wrong_ids = quiz_result.get("wrong_word_ids", [])
            if not wrong_ids:
                flash("There are no missed words to retry from the last quiz.", "info")
                return redirect(url_for("quiz"))
            resolution = build_questions_with_fallback(
                total_questions=min(len(wrong_ids), 10),
                quiz_type=quiz_result.get("quiz_type", "multiple_choice"),
                difficulty=quiz_result.get("difficulty", "Mixed"),
                word_source=quiz_result.get("word_source", "mixed_curriculum"),
                focus=quiz_result.get("focus", ""),
                specific_vocabulary_ids=wrong_ids,
            )
            questions = resolution["questions"]
            if not questions:
                flash("Could not build a retry quiz from the previous misses.", "info")
                return redirect(url_for("quiz"))
            session["quiz_state"] = {
                "questions": questions,
                "target_count": len(questions),
                "current_index": 0,
                "score": 0,
                "answers": [],
                "quiz_type": quiz_result.get("quiz_type", "multiple_choice"),
                "difficulty": quiz_result.get("difficulty", "Mixed"),
                "word_source": quiz_result.get("word_source", "mixed_curriculum"),
                "focus": quiz_result.get("focus", ""),
                "used_vocabulary_ids": [q["vocabulary_id"] for q in questions if q.get("vocabulary_id")],
                "started_at": quiz_started_at(),
                "retry_of_quiz_id": quiz_result.get("history_id"),
            }
            session.pop("quiz_result", None)
            return redirect(url_for("quiz_start"))

        if request.method == "POST" and not quiz_state:
            quiz_type = clean_text(request.form.get("quiz_type")) or "multiple_choice"
            word_source = clean_text(request.form.get("word_source")) or "mixed_curriculum"
            # Retire unseen_vocabulary silently — redirect to mixed_curriculum
            if word_source == "unseen_vocabulary":
                word_source = "mixed_curriculum"
            difficulty = clean_text(request.form.get("difficulty")) or "Mixed"
            focus = clean_text(request.form.get("focus") or request.form.get("custom_quiz_instruction"))
            try:
                question_count = int(request.form.get("question_count", "5"))
            except (TypeError, ValueError):
                question_count = 5
            if question_count not in QUESTION_COUNTS:
                question_count = 5

            # ── Educational validation: check quizable vocabulary count ───
            available = count_quizable_vocabularies(
                user_id=current_user.id,
                quiz_type=quiz_type,
                level=difficulty,
                word_source=word_source,
            )
            if available == 0:
                flash(
                    "No quiz-ready vocabulary found for this selection. "
                    "Try Mixed Curriculum or generate flashcards first to build your cache.",
                    "info",
                )
                return redirect(url_for("quiz"))
            if available < question_count:
                flash(
                    f"Only {available} quiz question{'s' if available != 1 else ''} are currently "
                    f"available for this selection. Starting a shorter quiz for you.",
                    "info",
                )
                question_count = available

            # ── Instant startup: generate first 2 questions immediately ───
            warmup = session.pop("quiz_warmup", None)
            signature = quiz_signature(quiz_type, word_source, difficulty, question_count, focus)
            initial_count = min(2, question_count)
            if warmup and warmup.get("signature") == signature:
                initial_questions = warmup.get("questions", [])[:initial_count]
            else:
                initial_resolution = build_questions_with_fallback(
                    initial_count, quiz_type, difficulty, word_source, focus
                )
                initial_questions = initial_resolution["questions"]
                # Update word_source/difficulty from resolved fallback
                word_source = initial_resolution.get("word_source", word_source)
                difficulty = initial_resolution.get("difficulty", difficulty)
                if initial_resolution.get("used_fallback"):
                    flash("That source was light, so we used the nearest available curriculum words.", "info")

            if not initial_questions:
                flash("No database vocabulary is ready for that quiz yet. Try Mixed Curriculum or generate flashcards first.", "info")
                return redirect(url_for("quiz"))

            session["quiz_state"] = {
                "questions": initial_questions,
                "target_count": question_count,
                "current_index": 0,
                "score": 0,
                "answers": [],
                "quiz_type": quiz_type,
                "difficulty": difficulty,
                "word_source": word_source,
                "focus": focus,
                "used_vocabulary_ids": [q["vocabulary_id"] for q in initial_questions if q.get("vocabulary_id")],
                "started_at": quiz_started_at(),
            }
            session.pop("quiz_result", None)
            return redirect(url_for("quiz_start"))

        if request.method == "POST":
            if not quiz_state:
                flash("No active quiz was found. Start a new quiz.", "info")
                return redirect(url_for("quiz"))
            if request.form.get("action") == "quit":
                finalize_quiz_result(quiz_state, mark_quit=True)
                return redirect(url_for("quiz", result=1))

            current_question = quiz_state["questions"][quiz_state["current_index"]]
            submitted = clean_text(request.form.get("answer"))
            correct = clean_text(current_question["answer"])
            is_correct = submitted.lower() == correct.lower()
            quiz_state["answers"].append(
                {
                    "prompt": current_question["prompt"],
                    "submitted": submitted,
                    "correct": current_question["answer"],
                    "is_correct": is_correct,
                    "question_type": current_question["question_type"],
                    "user_word_id": current_question.get("user_word_id"),
                    "vocabulary_id": current_question.get("vocabulary_id"),
                    "word": current_question.get("word"),
                    "explanation": current_question.get("explanation"),
                }
            )
            if is_correct:
                quiz_state["score"] += 1
            quiz_state["current_index"] += 1
            if quiz_state["current_index"] >= len(quiz_state["questions"]) and len(quiz_state["questions"]) < quiz_state.get("target_count", len(quiz_state["questions"])):
                append_quiz_batch(quiz_state, batch_size=3)
            if quiz_state["current_index"] >= len(quiz_state["questions"]):
                finalize_quiz_result(quiz_state)
                return redirect(url_for("quiz", result=1))
            session["quiz_state"] = quiz_state
            return redirect(url_for("quiz_start"))

        if not quiz_state:
            return redirect(url_for("quiz"))
        current_question = quiz_state["questions"][quiz_state["current_index"]]
        return render_template(
            "quiz.html",
            question=current_question,
            question_number=quiz_state["current_index"] + 1,
            total_questions=quiz_state.get("target_count", len(quiz_state["questions"])),
            score=quiz_state["score"],
            quiz_setup=None,
            quiz_result=None,
            quiz_meta={
                "quiz_type": quiz_state.get("quiz_type", "multiple_choice"),
                "difficulty": quiz_state.get("difficulty", "Mixed"),
                "word_source": quiz_state.get("word_source", "mixed_curriculum"),
                "focus": quiz_state.get("focus", ""),
            },
        )

    @app.route("/quiz/warmup", methods=["POST"])
    @login_required
    def quiz_warmup():
        questions = build_curriculum_quiz_questions(current_user.id, total_questions=3, quiz_type="multiple_choice", level="Mixed", word_source="mixed_curriculum")
        session["quiz_warmup"] = {
            "signature": quiz_signature("multiple_choice", "mixed_curriculum", "Mixed", 5, ""),
            "questions": questions,
        }
        session.modified = True
        return jsonify({"status": "ok", "generated": len(questions), "used_fallback": False})

    @app.route("/quiz/prefetch", methods=["POST"])
    @login_required
    def quiz_prefetch():
        quiz_state = session.get("quiz_state")
        if not quiz_state:
            return jsonify({"status": "error", "generated": 0}), 404
        generated = append_quiz_batch(quiz_state, batch_size=3)
        session["quiz_state"] = quiz_state
        session.modified = True
        return jsonify({"status": "ok", "generated": generated, "available_questions": len(quiz_state["questions"]), "target_count": quiz_state.get("target_count", len(quiz_state["questions"]))})
