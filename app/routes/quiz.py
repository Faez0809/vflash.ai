from datetime import date, datetime
import json

from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models import QuizHistory, UserWordProgress, SearchVocabulary, db
from app.services.quiz_engine import (
    LEVEL_OPTIONS,
    QUESTION_COUNTS,
    QUIZ_TYPES,
    WORD_SOURCES,
    collect_quiz_vocabularies,
    generate_question_for_item,
    quiz_started_at,
)
from app.services.stats import clean_text


def register(app):

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_all_questions(vocab_list, quiz_type, user_id):
        """
        Generate every question synchronously before creating a session.
        Returns a list of valid question dicts (may be shorter than vocab_list
        if some words fail generation).
        """
        questions = []
        for item in vocab_list:
            q = generate_question_for_item(
                item_id=item["id"],
                is_search=item["is_search"],
                quiz_type=quiz_type,
                user_id=user_id,
            )
            if q:
                questions.append(q)
                app.logger.info(
                    f"[Quiz] Generated question {len(questions)}: word='{q.get('word')}'"
                )
            else:
                app.logger.warning(
                    f"[Quiz] Skipped word id={item['id']} — generation returned None"
                )
        app.logger.info(
            f"[Quiz] Generation complete. Total generated: {len(questions)} / {len(vocab_list)}"
        )
        return questions

    def _append_pending_questions(quiz_state, limit=2):
        pending = list(quiz_state.get("pending_vocab", []))
        if not pending:
            return 0

        questions = quiz_state.setdefault("questions", [])
        used_words = {str(q.get("word", "")).lower() for q in questions}
        generated = 0
        while pending and generated < limit:
            item = pending.pop(0)
            q = generate_question_for_item(
                item_id=item["id"],
                is_search=item["is_search"],
                quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
                user_id=current_user.id,
            )
            if not q or str(q.get("word", "")).lower() in used_words:
                continue
            questions.append(q)
            used_words.add(str(q.get("word", "")).lower())
            generated += 1

        quiz_state["pending_vocab"] = pending
        quiz_state["questions"] = questions
        return generated

    def _log_session_state(quiz_state, label=""):
        """Emit a structured debug log of the current quiz session state."""
        prefix = f"[Quiz SessionState{' ' + label if label else ''}]"
        app.logger.info(
            f"{prefix} state={quiz_state.get('state')} "
            f"current_index={quiz_state.get('current_index')} "
            f"questions.length={len(quiz_state.get('questions', []))} "
            f"answers.length={len(quiz_state.get('answers', []))} "
            f"score={quiz_state.get('score')} "
            f"completed={quiz_state.get('completed', False)}"
        )

    def finalize_quiz_result(quiz_state, mark_quit=False):
        answered_count = len(quiz_state["answers"])
        total_questions = quiz_state.get("configured_total_questions") or len(quiz_state["questions"])
        wrong_answers = [a for a in quiz_state["answers"] if not a["is_correct"]]
        wrong_vocabulary_ids = sorted({
            a.get("vocabulary_id")
            for a in wrong_answers
            if a.get("vocabulary_id")
        })
        for vocabulary_id in wrong_vocabulary_ids:
            progress = UserWordProgress.query.filter_by(
                user_id=current_user.id, vocabulary_id=vocabulary_id
            ).first()
            if progress is not None:
                progress.is_difficult = True
                progress.times_reviewed = (progress.times_reviewed or 0) + 1
                progress.updated_at = datetime.utcnow()

        history = QuizHistory(
            user_id=current_user.id,
            quiz_type=quiz_state.get("quiz_type", "multiple_choice"),
            score=quiz_state["score"],
            total_questions=answered_count or total_questions,
            answered_questions=answered_count,
            configured_total_questions=total_questions,
            was_quit=mark_quit,
            mistakes_json=json.dumps(wrong_answers),
            weak_vocabulary_ids=",".join(str(i) for i in wrong_vocabulary_ids),
            completion_seconds=max(
                0,
                int(datetime.utcnow().timestamp())
                - int(quiz_state.get("started_at", quiz_started_at())),
            ),
            retry_of_quiz_id=quiz_state.get("retry_of_quiz_id"),
            created_at=date.today(),
        )
        db.session.add(history)
        db.session.commit()

        session["quiz_result"] = {
            "score": quiz_state["score"],
            "total_questions": answered_count or total_questions,
            "configured_total_questions": total_questions,
            "answers": quiz_state["answers"],
            "quiz_type": quiz_state.get("quiz_type", "multiple_choice"),
            "difficulty": quiz_state.get("difficulty", "Mixed"),
            "word_source": quiz_state.get("word_source", "mixed_curriculum"),
            "focus": quiz_state.get("focus", ""),
            "accuracy": round((quiz_state["score"] / answered_count) * 100)
            if answered_count
            else 0,
            "correct_count": quiz_state["score"],
            "wrong_count": max(0, answered_count - quiz_state["score"]),
            "wrong_word_ids": wrong_vocabulary_ids,
            "was_quit": mark_quit,
            "history_id": history.id,
        }
        session.pop("quiz_state", None)
        app.logger.info(
            f"[Quiz] Finalized. score={quiz_state['score']}/{answered_count or total_questions} "
            f"quit={mark_quit}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # ROUTES
    # ─────────────────────────────────────────────────────────────────────────

    @app.route("/quiz", methods=["GET"])
    @login_required
    def quiz():
        if request.args.get("reset") == "1":
            session.pop("quiz_state", None)
            session.pop("quiz_result", None)
            if request.args.get("failed") == "1":
                return redirect(url_for("quiz", failed=1))
            return redirect(url_for("quiz"))

        if request.args.get("failed") == "1":
            flash(
                "Quiz service is temporarily unavailable. "
                "Please try again later or use Flashcards/Search.",
                "info",
            )
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

        # ── RETRY wrong-answer quiz ──────────────────────────────────────────
        if request.args.get("retry") == "wrong":
            quiz_result = session.get("quiz_result") or {}
            wrong_ids = quiz_result.get("wrong_word_ids", [])
            if not wrong_ids:
                flash("There are no missed words to retry from the last quiz.", "info")
                return redirect(url_for("quiz"))

            retry_quiz_type = quiz_result.get("quiz_type", "multiple_choice")
            vocab_list = [{"id": wid, "word": "", "is_search": False} for wid in wrong_ids[:10]]
            app.logger.info(
                f"[Quiz] Retry — vocab candidates: {len(vocab_list)}"
            )

            # Generate ALL retry questions upfront
            questions = _generate_all_questions(vocab_list, retry_quiz_type, current_user.id)
            app.logger.info(
                f"[Quiz] Retry — questions generated: {len(questions)}"
            )

            if not questions:
                flash(
                    "Quiz questions could not be prepared right now. "
                    "Please try another source or use Flashcards/Search.",
                    "info",
                )
                return redirect(url_for("quiz"))

            session["quiz_state"] = {
                "state": "active",
                "questions": questions,
                "current_index": 0,
                "score": 0,
                "answers": [],
                "completed": False,
                "quiz_type": retry_quiz_type,
                "difficulty": quiz_result.get("difficulty", "Mixed"),
                "word_source": quiz_result.get("word_source", "mixed_curriculum"),
                "focus": quiz_result.get("focus", ""),
                "started_at": quiz_started_at(),
                "retry_of_quiz_id": quiz_result.get("history_id"),
            }
            session.pop("quiz_result", None)
            _log_session_state(session["quiz_state"], label="RetryCreated")
            return redirect(url_for("quiz_start"))

        # ── START new quiz (POST from setup form) ────────────────────────────
        if request.method == "POST" and not quiz_state:
            quiz_type = clean_text(request.form.get("quiz_type")) or "multiple_choice"
            word_source = clean_text(request.form.get("word_source")) or "mixed_curriculum"
            if word_source == "unseen_vocabulary":
                word_source = "mixed_curriculum"
            difficulty = clean_text(request.form.get("difficulty")) or "Mixed"
            focus = clean_text(
                request.form.get("focus") or request.form.get("custom_quiz_instruction")
            )
            try:
                question_count = int(request.form.get("question_count", "5"))
            except (TypeError, ValueError):
                question_count = 5
            if question_count not in QUESTION_COUNTS:
                question_count = 5

            # Step 1: Collect vocabulary entries
            vocab_list = []
            if word_source == "search_vocabulary":
                rows = (
                    SearchVocabulary.query
                    .filter(
                        SearchVocabulary.searched_by_user_id == current_user.id,
                        SearchVocabulary.is_fully_enriched.is_(True),
                        SearchVocabulary.enrichment_score >= 0.8,
                        SearchVocabulary.definition.isnot(None),
                        SearchVocabulary.bangla_meaning.isnot(None),
                        SearchVocabulary.example_sentence.isnot(None),
                        SearchVocabulary.part_of_speech.isnot(None),
                    )
                    .order_by(SearchVocabulary.created_at.desc())
                    .limit(question_count)
                    .all()
                )
                vocab_list = [{"id": row.id, "word": row.word, "is_search": True} for row in rows]
            else:
                vocabs = collect_quiz_vocabularies(
                    user_id=current_user.id,
                    count=question_count,
                    level=difficulty,
                    word_source=word_source,
                )
                vocab_list = [{"id": v.id, "word": v.word, "is_search": False} for v in vocabs]

            app.logger.info(
                f"[Quiz] Start — requested={question_count} collected={len(vocab_list)} "
                f"source={word_source} level={difficulty}"
            )

            if not vocab_list:
                flash(
                    "No quiz-ready vocabulary found for this selection. "
                    "Try Mixed Curriculum or generate flashcards first to build your cache.",
                    "info",
                )
                return redirect(url_for("quiz"))

            # Generate the first valid question now; background prefetch appends the rest.
            first_state = {
                "state": "active",
                "questions": [],
                "pending_vocab": vocab_list,
                "current_index": 0,
                "score": 0,
                "answers": [],
                "completed": False,
                "quiz_type": quiz_type,
                "difficulty": difficulty,
                "word_source": word_source,
                "focus": focus,
                "started_at": quiz_started_at(),
                "configured_total_questions": question_count,
            }
            _append_pending_questions(first_state, limit=1)
            questions = first_state["questions"]
            app.logger.info(
                f"[Quiz] Start — generated={len(questions)} questions"
            )

            if not questions:
                flash(
                    "Quiz questions could not be prepared right now. "
                    "Please try another source or use Flashcards/Search.",
                    "info",
                )
                return redirect(url_for("quiz"))

            # Create a stable session with queued vocabulary for progressive loading.
            session["quiz_state"] = first_state
            session.pop("quiz_result", None)
            _log_session_state(session["quiz_state"], label="SessionCreated")
            return redirect(url_for("quiz_start"))

        # ── POST with existing session (answer submission or quit) ───────────
        if request.method == "POST":
            if not quiz_state:
                flash("No active quiz was found. Start a new quiz.", "info")
                return redirect(url_for("quiz"))

            if request.form.get("action") == "quit":
                _log_session_state(quiz_state, label="Quit")
                finalize_quiz_result(quiz_state, mark_quit=True)
                return redirect(url_for("quiz", result=1))

            # Safety: validate current_index before accessing questions array
            questions = quiz_state.get("questions", [])
            current_index = quiz_state.get("current_index", 0)

            if not questions:
                app.logger.error(
                    "[Quiz] POST received but questions list is empty. "
                    "Aborting quiz — this should never happen."
                )
                session.pop("quiz_state", None)
                flash("Quiz state is invalid. Please start a new quiz.", "info")
                return redirect(url_for("quiz"))

            if current_index >= len(questions):
                app.logger.error(
                    f"[Quiz] POST received but current_index={current_index} >= "
                    f"questions.length={len(questions)}. Aborting."
                )
                session.pop("quiz_state", None)
                flash("Quiz state is invalid. Please start a new quiz.", "info")
                return redirect(url_for("quiz"))

            # Record the answer
            current_question = questions[current_index]
            submitted = clean_text(request.form.get("answer"))
            correct = clean_text(current_question["answer"])
            is_correct = submitted.lower() == correct.lower()

            quiz_state["answers"].append({
                "prompt": current_question["prompt"],
                "submitted": submitted,
                "correct": current_question["answer"],
                "is_correct": is_correct,
                "question_type": current_question["question_type"],
                "user_word_id": current_question.get("user_word_id"),
                "vocabulary_id": current_question.get("vocabulary_id"),
                "word": current_question.get("word"),
                "explanation": current_question.get("explanation"),
            })

            if is_correct:
                quiz_state["score"] += 1

            quiz_state["current_index"] += 1
            new_index = quiz_state["current_index"]
            if new_index >= len(questions) and quiz_state.get("pending_vocab"):
                _append_pending_questions(quiz_state, limit=1)
                questions = quiz_state.get("questions", [])

            app.logger.info(
                f"[Quiz] Answer recorded. correct={is_correct} "
                f"new_index={new_index} total_questions={len(questions)}"
            )

            # Check completion — ONLY when we have exhausted all pre-generated questions
            if new_index >= len(questions):
                quiz_state["state"] = "completed"
                quiz_state["completed"] = True
                _log_session_state(quiz_state, label="Completing")
                finalize_quiz_result(quiz_state)
                return redirect(url_for("quiz", result=1))

            # More questions remain — persist state and show next question
            session["quiz_state"] = quiz_state
            session.modified = True
            _log_session_state(quiz_state, label="NextQuestion")
            return redirect(url_for("quiz_start"))

        # ── GET — render the active quiz question ────────────────────────────
        if not quiz_state:
            return redirect(url_for("quiz"))

        state = quiz_state.get("state", "active")
        questions = quiz_state.get("questions", [])
        current_index = quiz_state.get("current_index", 0)

        # Log the state every time the quiz page is loaded
        _log_session_state(quiz_state, label="GET")

        if current_index >= len(questions) and quiz_state.get("pending_vocab"):
            _append_pending_questions(quiz_state, limit=1)
            session["quiz_state"] = quiz_state
            session.modified = True
            questions = quiz_state.get("questions", [])

        # Guard: session exists but has no questions — stale/invalid session
        if not questions:
            app.logger.error(
                "[Quiz] GET: quiz_state exists but questions list is empty. "
                "Clearing stale session."
            )
            session.pop("quiz_state", None)
            flash(
                "Quiz questions could not be prepared right now. "
                "Please try another source or use Flashcards/Search.",
                "info",
            )
            return redirect(url_for("quiz"))

        # Guard: current_index out of bounds — corrupt session
        if current_index >= len(questions):
            app.logger.error(
                f"[Quiz] GET: current_index={current_index} >= questions.length={len(questions)}. "
                f"state={state} completed={quiz_state.get('completed')}. Clearing session."
            )
            session.pop("quiz_state", None)
            flash(
                "Quiz session ended unexpectedly. Please start a new quiz.",
                "info",
            )
            return redirect(url_for("quiz"))

        # Guard: state is already completed — finalize if not already done
        if state == "completed" or quiz_state.get("completed"):
            app.logger.warning(
                "[Quiz] GET: session has completed=True but quiz_result was not yet set. "
                "Finalizing now."
            )
            if not session.get("quiz_result"):
                finalize_quiz_result(quiz_state)
            else:
                session.pop("quiz_state", None)
            return redirect(url_for("quiz", result=1))

        # Guard: failed state
        if state == "failed":
            session.pop("quiz_state", None)
            return redirect(url_for("quiz", reset=1, failed=1))

        # All guards passed — render the active question
        app.logger.info(
            f"[Quiz] Rendering question {current_index + 1}/{quiz_state.get('configured_total_questions') or len(questions)}: "
            f"word='{questions[current_index].get('word')}'"
        )
        current_question = questions[current_index]
        return render_template(
            "quiz.html",
            state="active",
            question=current_question,
            question_number=current_index + 1,
            total_questions=quiz_state.get("configured_total_questions") or len(questions),
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

    # ── Warmup endpoint (stub — kept for compatibility) ──────────────────────
    @app.route("/quiz/warmup", methods=["POST"])
    @login_required
    def quiz_warmup():
        return jsonify({"status": "ok", "generated": 0, "used_fallback": False})

    # ── Prefetch endpoint (disabled — returns no-op so JS doesn't error) ─────
    # Progressive loading is temporarily disabled until core gameplay is stable.
    @app.route("/quiz/prefetch", methods=["POST"])
    @login_required
    def quiz_prefetch():
        """
        Prefetch is disabled while we stabilize the quiz session lifecycle.
        Returns a no-op response so the frontend prefetch call silently succeeds.
        All questions are now generated upfront before session creation.
        """
        quiz_state = session.get("quiz_state")
        if not quiz_state:
            return jsonify({"status": "ok", "generated": 0, "available_questions": 0, "target_count": 0})
        generated = _append_pending_questions(quiz_state, limit=3)
        session["quiz_state"] = quiz_state
        session.modified = True
        questions = quiz_state.get("questions", [])
        return jsonify({
            "status": "ok",
            "state": quiz_state.get("state", "active"),
            "generated": generated,
            "available_questions": len(questions),
            "target_count": quiz_state.get("configured_total_questions") or len(questions),
        })
