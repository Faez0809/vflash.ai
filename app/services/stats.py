from collections import Counter
from datetime import date, timedelta
import random
import re

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
    recent_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    recent_days.sort(key=lambda item: item.weekday())

    weekly_activity = []
    for day in recent_days:
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


def pluralize(count, singular, plural=None):
    """Return a count-aware label like '1 word' or '2 words'."""
    chosen = singular if count == 1 else (plural or f"{singular}s")
    return f"{count} {chosen}"


def normalize_quiz_subtitle(subtitle, question_type):
    """Keep quiz subtitles short and natural."""
    subtitle = clean_text(subtitle)
    if question_type == "fill_blank":
        lowered = subtitle.lower()
        if not subtitle or "target word" in lowered or "find" in lowered:
            return "Type the missing word"
    elif not subtitle:
        return "Choose the correct meaning"
    return subtitle.rstrip(" .:-")


def normalize_fill_blank_prompt(prompt):
    """Remove trailing placeholder marks and normalize spacing."""
    prompt = clean_text(prompt)
    if not prompt:
        return prompt

    prompt = re.sub(r"\s+([,.;!?])", r"\1", prompt)
    prompt = re.sub(r"(?:\s*[_-]{2,}\s*)+$", "", prompt).strip()
    prompt = re.sub(r"\s{2,}", " ", prompt)
    return prompt


def is_relevant_fill_blank_sentence(sentence_text, word_text):
    """Ensure fill-in-the-blank sentences actually relate to the target word."""
    sentence_text = clean_text(sentence_text)
    word_text = clean_text(word_text)
    if not sentence_text or not word_text:
        return False
    return re.search(rf"\b{re.escape(word_text)}\b", sentence_text, re.IGNORECASE) is not None


def build_mcq_distractors(correct_meaning, candidate_meanings):
    """Create distinct, non-empty distractors for meaning-based MCQs."""
    normalized_correct = clean_text(correct_meaning).lower()
    distractors = []
    seen = {normalized_correct}

    for item in candidate_meanings:
        cleaned = clean_text(item)
        lowered = cleaned.lower()
        if not cleaned or lowered in seen:
            continue
        seen.add(lowered)
        distractors.append(cleaned)
        if len(distractors) == 3:
            break

    return distractors


def build_fill_in_blank_sentence(word_text, sentence_text):
    """Create a simple fill-in-the-blank prompt for quiz mode."""
    sentence_text = clean_text(sentence_text)
    if not sentence_text:
        return "Complete the sentence with the best word."

    pattern = re.compile(rf"\b{re.escape(word_text)}\b", re.IGNORECASE)
    if pattern.search(sentence_text):
        return normalize_fill_blank_prompt(pattern.sub("_____", sentence_text, 1))
    return normalize_fill_blank_prompt(sentence_text)


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

        quiz_support = {}
        if question_type == "fill_blank":
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
            fallback_meanings = [candidate.word_entry.meaning for candidate in random.sample(pool, min(len(pool), 6))]
            distractors = build_mcq_distractors(word_entry.meaning, fallback_meanings)
            if len(distractors) < 3:
                extra_meanings = [candidate.word_entry.meaning for candidate in pool]
                distractors = build_mcq_distractors(word_entry.meaning, fallback_meanings + extra_meanings)
            if len(distractors) < 3:
                continue
            options = [word_entry.meaning] + distractors[:3]
            random.shuffle(options)
            questions.append(
                {
                    "question_type": question_type,
                    "user_word_id": item.id,
                    "prompt": word_entry.word,
                    "subtitle": "Choose the correct meaning",
                    "answer": word_entry.meaning,
                    "options": options,
                }
            )
        else:
            fill_blank_sentence = quiz_support.get("fill_blank_sentence") or word_entry.sentence
            if not is_relevant_fill_blank_sentence(fill_blank_sentence, word_entry.word):
                fill_blank_sentence = word_entry.sentence or word_entry.word
            questions.append(
                {
                    "question_type": question_type,
                    "user_word_id": item.id,
                    "prompt": normalize_fill_blank_prompt(
                        build_fill_in_blank_sentence(word_entry.word, fill_blank_sentence)
                    ),
                    "subtitle": normalize_quiz_subtitle(quiz_support.get("subtitle"), question_type),
                    "answer": word_entry.word,
                    "meaning": word_entry.meaning,
                    "options": [],
                }
            )

        used_word_ids.add(item.id)

    return questions[:total_questions]
