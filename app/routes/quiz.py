from datetime import date

from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models import QuizHistory, db
from app.services.learning_content import FALLBACK_CONTINUE_MESSAGE, ensure_starter_pack_for_user
from app.services.stats import build_quiz_questions, clean_text


def register(app):
    def build_quiz_warmup_signature(
        quiz_type="multiple_choice",
        word_source="my_words",
        difficulty="All",
        question_count=10,
        custom_instruction="",
    ):
        return "::".join(
            [
                clean_text(quiz_type) or "multiple_choice",
                clean_text(word_source) or "my_words",
                clean_text(difficulty) or "All",
                str(question_count or 10),
                clean_text(custom_instruction),
            ]
        )

    def build_quiz_questions_with_fallback(
        *,
        total_questions,
        quiz_type,
        difficulty,
        word_source,
        custom_instruction="",
    ):
        source_candidates = []
        for candidate in [word_source, "weak_words", "difficult_words", "my_words", "todays_words"]:
            if candidate not in source_candidates:
                source_candidates.append(candidate)

        difficulty_candidates = []
        for candidate in [difficulty, "All"]:
            if candidate and candidate not in difficulty_candidates:
                difficulty_candidates.append(candidate)
        if not difficulty_candidates:
            difficulty_candidates.append("All")

        for source_candidate in source_candidates:
            for difficulty_candidate in difficulty_candidates:
                questions = build_quiz_questions(
                    current_user.id,
                    total_questions=total_questions,
                    quiz_type=quiz_type,
                    difficulty=difficulty_candidate,
                    word_source=source_candidate,
                    custom_instruction=custom_instruction,
                )
                if questions:
                    return {
                        "questions": questions,
                        "word_source": source_candidate,
                        "difficulty": difficulty_candidate,
                        "used_fallback": source_candidate != word_source or difficulty_candidate != difficulty,
                    }

        starter_pack = ensure_starter_pack_for_user(current_user.id, custom_instruction)
        if starter_pack["created"]:
            questions = build_quiz_questions(
                current_user.id,
                total_questions=total_questions,
                quiz_type=quiz_type,
                difficulty="All",
                word_source="my_words",
                custom_instruction=custom_instruction,
            )
            if questions:
                return {
                    "questions": questions,
                    "word_source": "my_words",
                    "difficulty": "All",
                    "used_fallback": True,
                }

        return {
            "questions": [],
            "word_source": word_source,
            "difficulty": difficulty,
            "used_fallback": False,
        }

    def append_quiz_batch(quiz_state, batch_size=3):
        remaining = max(0, quiz_state["target_count"] - len(quiz_state["questions"]))
        if remaining == 0:
            return 0

        source_candidates = []
        for candidate in [
            quiz_state.get("word_source", "my_words"),
            "weak_words",
            "difficult_words",
            "my_words",
            "todays_words",
        ]:
            if candidate not in source_candidates:
                source_candidates.append(candidate)

        difficulty_candidates = []
        for candidate in [quiz_state.get("difficulty", "All"), "All"]:
            if candidate and candidate not in difficulty_candidates:
                difficulty_candidates.append(candidate)

        new_questions = []
        for source_candidate in source_candidates:
            for difficulty_candidate in difficulty_candidates:
                new_questions = build_quiz_questions(
                    current_user.id,
                    total_questions=min(batch_size, remaining),
                    quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
                    difficulty=difficulty_candidate,
                    word_source=source_candidate,
                    custom_instruction=quiz_state.get("custom_instruction", ""),
                    exclude_user_word_ids=quiz_state.get("used_word_ids", []),
                )
                if new_questions:
                    break
            if new_questions:
                break

        if not new_questions:
            return 0

        quiz_state["questions"].extend(new_questions)
        quiz_state["used_word_ids"] = quiz_state.get("used_word_ids", []) + [
            question.get("user_word_id")
            for question in new_questions
            if question.get("user_word_id")
        ]
        return len(new_questions)

    def finalize_quiz_result(quiz_state, mark_quit=False):
        answered_count = len(quiz_state["answers"])
        configured_total_questions = quiz_state.get("target_count", len(quiz_state["questions"]))
        history = QuizHistory(
            user_id=current_user.id,
            quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
            score=quiz_state["score"],
            total_questions=answered_count or len(quiz_state["questions"]),
            answered_questions=answered_count,
            configured_total_questions=configured_total_questions,
            was_quit=mark_quit,
            created_at=date.today(),
        )
        db.session.add(history)
        db.session.commit()

        wrong_word_ids = [
            answer["user_word_id"]
            for answer in quiz_state["answers"]
            if not answer["is_correct"] and answer.get("user_word_id")
        ]
        session["quiz_result"] = {
            "score": quiz_state["score"],
            "total_questions": answered_count or len(quiz_state["questions"]),
            "configured_total_questions": configured_total_questions,
            "answers": quiz_state["answers"],
            "quiz_type": quiz_state.get("quiz_type", "multiple_choice"),
            "difficulty": quiz_state.get("difficulty", "All"),
            "word_source": quiz_state.get("word_source", "my_words"),
            "custom_instruction": quiz_state.get("custom_instruction", ""),
            "accuracy": round((quiz_state["score"] / answered_count) * 100) if answered_count else 0,
            "correct_count": quiz_state["score"],
            "wrong_count": max(0, answered_count - quiz_state["score"]),
            "wrong_word_ids": wrong_word_ids,
            "was_quit": mark_quit,
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

        # Explicitly popping previous results if visiting quiz freshly to ensure setup loads
        session.pop("quiz_result", None)

        return render_template(
            "quiz.html",
            quiz_setup={
                "quiz_types": [
                    ("multiple_choice", "MCQ"),
                    ("fill_blank", "Fill in the Blank"),
                    ("mixed", "Mixed Quiz"),
                ],
                "word_sources": [
                    ("todays_words", "Today's Words"),
                    ("my_words", "My Words"),
                    ("difficult_words", "Difficult Words"),
                    ("weak_words", "Weak Words"),
                ],
                "difficulty_options": ["All", "Beginner", "Intermediate", "Advanced"],
                "question_counts": [5, 10, 15],
                "has_resume": bool(quiz_state),
                "resume_progress": (
                    {
                        "current_index": quiz_state.get("current_index", 0),
                        "total_questions": len(quiz_state.get("questions", [])),
                        "score": quiz_state.get("score", 0),
                    }
                    if quiz_state
                    else None
                ),
            },
            quiz_result=None,
        )

    @app.route("/quiz/start", methods=["GET", "POST"])
    @login_required
    def quiz_start():
        quiz_state = session.get("quiz_state")

        if request.args.get("retry") == "wrong":
            quiz_result = session.get("quiz_result")
            wrong_word_ids = quiz_result.get("wrong_word_ids", []) if quiz_result else []
            if not wrong_word_ids:
                flash("There are no wrong words to retry from the last quiz.", "info")
                return redirect(url_for("quiz"))

            questions = build_quiz_questions(
                current_user.id,
                total_questions=min(len(wrong_word_ids), 10),
                quiz_type=quiz_result.get("quiz_type", "multiple_choice"),
                difficulty=quiz_result.get("difficulty", "All"),
                word_source=quiz_result.get("word_source", "my_words"),
                specific_user_word_ids=wrong_word_ids,
                custom_instruction=quiz_result.get("custom_instruction", ""),
            )
            if not questions:
                flash("Could not build a retry quiz from the previous wrong answers.", "info")
                return redirect(url_for("quiz"))

            session["quiz_state"] = {
                "questions": questions,
                "target_count": len(questions),
                "current_index": 0,
                "score": 0,
                "answers": [],
                "quiz_type": quiz_result.get("quiz_type", "multiple_choice"),
                "difficulty": quiz_result.get("difficulty", "All"),
                "word_source": quiz_result.get("word_source", "my_words"),
                "custom_instruction": quiz_result.get("custom_instruction", ""),
                "used_word_ids": [question.get("user_word_id") for question in questions if question.get("user_word_id")],
            }
            session.pop("quiz_result", None)
            return redirect(url_for("quiz_start"))

        if request.method == "POST" and not quiz_state:
            quiz_type = clean_text(request.form.get("quiz_type")) or "multiple_choice"
            word_source = clean_text(request.form.get("word_source")) or "my_words"
            difficulty = clean_text(request.form.get("difficulty")) or "All"
            custom_instruction = clean_text(request.form.get("custom_quiz_instruction"))

            try:
                question_count = int(request.form.get("question_count", "10"))
            except (TypeError, ValueError):
                question_count = 10

            if question_count not in {5, 10, 15}:
                question_count = 10

            warmup_signature = build_quiz_warmup_signature(
                quiz_type=quiz_type,
                word_source=word_source,
                difficulty=difficulty,
                question_count=question_count,
                custom_instruction=custom_instruction,
            )
            warmup_cache = session.pop("quiz_warmup", None)
            warmup_questions = []
            if warmup_cache and warmup_cache.get("signature") == warmup_signature:
                warmup_questions = warmup_cache.get("questions", [])

            if warmup_questions:
                resolution = {
                    "questions": warmup_questions,
                    "word_source": word_source,
                    "difficulty": difficulty,
                    "used_fallback": False,
                }
            else:
                resolution = build_quiz_questions_with_fallback(
                    total_questions=min(3, question_count),
                    quiz_type=quiz_type,
                    difficulty=difficulty,
                    word_source=word_source,
                    custom_instruction=custom_instruction,
                )

            questions = resolution["questions"]
            if not questions:
                flash("We could not prepare a quiz right now. Try again in a moment.", "info")
                return redirect(url_for("quiz"))

            if resolution["used_fallback"]:
                flash(FALLBACK_CONTINUE_MESSAGE, "info")

            session["quiz_state"] = {
                "questions": questions,
                "target_count": question_count,
                "current_index": 0,
                "score": 0,
                "answers": [],
                "quiz_type": quiz_type,
                "difficulty": resolution["difficulty"],
                "word_source": resolution["word_source"],
                "custom_instruction": custom_instruction,
                "used_word_ids": [question.get("user_word_id") for question in questions if question.get("user_word_id")],
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

            current_index = quiz_state["current_index"]
            current_question = quiz_state["questions"][current_index]
            submitted_answer = clean_text(request.form.get("answer")).lower()
            correct_answer = clean_text(current_question["answer"]).lower()
            
            if current_question.get("question_type") == "fill_blank":
                from app.services.ai_generator import verify_answer_using_ai
                is_correct = verify_answer_using_ai(current_question["prompt"], correct_answer, submitted_answer)
            else:
                is_correct = submitted_answer == correct_answer


            quiz_state["answers"].append(
                {
                    "prompt": current_question["prompt"],
                    "submitted": submitted_answer,
                    "correct": current_question["answer"],
                    "is_correct": is_correct,
                    "question_type": current_question["question_type"],
                    "user_word_id": current_question.get("user_word_id"),
                }
            )
            if is_correct:
                quiz_state["score"] += 1

            quiz_state["current_index"] += 1
            if (
                quiz_state["current_index"] >= len(quiz_state["questions"])
                and len(quiz_state["questions"]) < quiz_state.get("target_count", len(quiz_state["questions"]))
            ):
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
                "difficulty": quiz_state.get("difficulty", "All"),
                "word_source": quiz_state.get("word_source", "my_words"),
                "custom_instruction": quiz_state.get("custom_instruction", ""),
            },
        )

    @app.route("/quiz/warmup", methods=["POST"])
    @login_required
    def quiz_warmup():
        question_count = 10
        resolution = build_quiz_questions_with_fallback(
            total_questions=min(3, question_count),
            quiz_type="multiple_choice",
            difficulty="All",
            word_source="my_words",
            custom_instruction="",
        )
        session["quiz_warmup"] = {
            "signature": build_quiz_warmup_signature(),
            "questions": resolution["questions"],
        }
        session.modified = True
        return jsonify(
            {
                "status": "ok",
                "generated": len(resolution["questions"]),
                "used_fallback": resolution["used_fallback"],
            }
        )

    @app.route("/quiz/prefetch", methods=["POST"])
    @login_required
    def quiz_prefetch():
        quiz_state = session.get("quiz_state")
        if not quiz_state:
            return jsonify({"status": "error", "generated": 0}), 404

        generated = append_quiz_batch(quiz_state, batch_size=3)
        session["quiz_state"] = quiz_state
        session.modified = True
        return jsonify(
            {
                "status": "ok",
                "generated": generated,
                "available_questions": len(quiz_state["questions"]),
                "target_count": quiz_state.get("target_count", len(quiz_state["questions"])),
            }
        )
