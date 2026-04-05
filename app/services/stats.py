from collections import Counter
from datetime import date, timedelta
import random

from sqlalchemy import or_

from app.models import UserWord, Word
from app.services.ai_generator import generate_quiz_question_support


def clean_text(value):
    """Normalize optional text fields coming from forms or AI responses."""
    if value is None:
        return ""
    return str(value).strip()


def get_study_streak(user_id):
    """Count consecutive days with study activity ending today."""
    user_activity = UserWord.query.filter_by(user_id=user_id).all()
    activity_dates = {
        activity_date
        for item in user_activity
        for activity_date in (item.added_date, item.last_reviewed, item.learned_at)
        if activity_date
    }
    if not activity_dates:
        return 0

    streak = 0
    current_day = date.today()
    while current_day in activity_dates:
        streak += 1
        current_day -= timedelta(days=1)
    return streak


def get_weekly_activity(user_id):
    """Return lightweight activity counts for the last 7 days."""
    user_activity = UserWord.query.filter_by(user_id=user_id).all()
    counts = Counter()
    for item in user_activity:
        for activity_date in (item.added_date, item.last_reviewed, item.learned_at):
            if activity_date:
                counts[activity_date] += 1

    today = date.today()
    weekly_activity = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        weekly_activity.append(
            {
                "label": day.strftime("%a"),
                "count": counts.get(day, 0),
            }
        )
    max_count = max((item["count"] for item in weekly_activity), default=0)
    for item in weekly_activity:
        item["height"] = 18 if max_count == 0 else max(18, round((item["count"] / max_count) * 100))
    return weekly_activity


def build_fill_in_blank_sentence(word_text, sentence_text):
    """Create a simple fill-in-the-blank prompt for quiz mode."""
    sentence_text = clean_text(sentence_text)
    if sentence_text and word_text.lower() in sentence_text.lower():
        return sentence_text.replace(word_text, "_____", 1).replace(word_text.capitalize(), "_____", 1)
    if sentence_text:
        return f"{sentence_text} (Target word hidden: _____)"
    return f"Fill in the blank with the correct word: _____ means {word_text}."


def build_quiz_questions(
    user_id,
    total_questions=10,
    quiz_type="mixed",
    difficulty=None,
    word_source="my_words",
    specific_user_word_ids=None,
    custom_instruction="",
    exclude_user_word_ids=None,
):
    """Create quiz questions from the user's saved words."""
    user_words_query = (
        UserWord.query.filter_by(user_id=user_id)
        .join(Word)
        .order_by(UserWord.added_date.desc(), Word.word.asc())
    )
    exclude_user_word_ids = {
        int(item)
        for item in (exclude_user_word_ids or [])
        if str(item).strip().isdigit()
    }

    if specific_user_word_ids:
        user_words_query = user_words_query.filter(UserWord.id.in_(specific_user_word_ids))
    elif word_source == "todays_words":
        user_words_query = user_words_query.filter(UserWord.added_date == date.today())
    elif word_source == "difficult_words":
        user_words_query = user_words_query.filter(UserWord.is_difficult.is_(True))
    elif word_source == "weak_words":
        user_words_query = user_words_query.filter(
            or_(
                UserWord.is_difficult.is_(True),
                UserWord.learned.is_(False),
            )
        )

    if difficulty and difficulty != "All":
        user_words_query = user_words_query.filter(Word.difficulty == difficulty)

    user_words = user_words_query.all()
    if exclude_user_word_ids:
        user_words = [item for item in user_words if item.id not in exclude_user_word_ids]
    if len(user_words) < 1:
        return []

    choice_question_types = {
        "multiple_choice": "multiple_choice",
        "fill_blank": "fill_blank",
        "mixed": "mixed",
    }
    quiz_type = choice_question_types.get(quiz_type, "mixed")

    if quiz_type in {"multiple_choice", "mixed"} and len(user_words) < 4:
        return []

    questions = []
    attempts = 0
    used_word_ids = set()

    while len(questions) < total_questions and attempts < total_questions * 4:
        attempts += 1
        available_items = [candidate for candidate in user_words if candidate.id not in used_word_ids]
        if not available_items:
            break

        item = random.choice(available_items)
        pool = [candidate for candidate in user_words if candidate.id != item.id]
        word_entry = item.word_entry
        if quiz_type == "mixed":
            question_type = random.choice(["multiple_choice", "fill_blank"])
        else:
            question_type = quiz_type

        quiz_support = generate_quiz_question_support(
            word=word_entry.word,
            meaning=word_entry.meaning,
            sentence=word_entry.sentence or "",
            difficulty=word_entry.difficulty or difficulty or "",
            custom_instruction=custom_instruction,
            quiz_type=question_type,
        )

        if question_type == "multiple_choice":
            if len(pool) < 3:
                continue
            distractors = quiz_support.get("distractors") or [candidate.word_entry.meaning for candidate in random.sample(pool, 3)]
            if len(distractors) < 3:
                fallback_meanings = [candidate.word_entry.meaning for candidate in random.sample(pool, 3)]
                distractors = (distractors + fallback_meanings)[:3]
            options = [word_entry.meaning] + distractors[:3]
            random.shuffle(options)
            questions.append(
                {
                    "question_type": question_type,
                    "user_word_id": item.id,
                    "prompt": quiz_support.get("question_prompt") or word_entry.word,
                    "subtitle": quiz_support.get("subtitle") or "Choose the correct meaning",
                    "answer": word_entry.meaning,
                    "options": options,
                }
            )
        else:
            fill_blank_sentence = quiz_support.get("fill_blank_sentence") or word_entry.sentence
            questions.append(
                {
                    "question_type": question_type,
                    "user_word_id": item.id,
                    "prompt": build_fill_in_blank_sentence(word_entry.word, fill_blank_sentence),
                    "subtitle": quiz_support.get("subtitle") or "Type the missing word",
                    "answer": word_entry.word,
                    "options": [],
                }
            )

        used_word_ids.add(item.id)

    return questions[:total_questions]
