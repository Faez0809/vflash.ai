import random
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from app.models import SearchVocabulary, UserWordProgress, VocabularyMaster, db
from app.services.vocabulary_platform import get_or_create_enrichment, normalize_level


QUIZ_TYPES = (
    ("multiple_choice", "MCQ"),
    ("meaning_match", "Meaning Match"),
    ("fill_blank", "Fill in the blank"),
    ("synonym_match", "Synonym Match"),
    ("reverse_meaning", "Reverse Meaning"),
    ("bangla_to_english", "Bangla to English"),
    ("english_to_bangla", "English to Bangla"),
)
WORD_SOURCES = (
    ("learned_words", "My Learned Words"),
    ("difficult_words", "Difficult / Review Words"),
    ("generated_words", "Generated Flashcard Words"),
    ("unseen_vocabulary", "Unseen Vocabulary"),
    ("mixed_curriculum", "Mixed Curriculum"),
    ("search_vocabulary", "Search Vocabulary"),
    ("level_curriculum", "Level-Based Curriculum"),
)
LEVEL_OPTIONS = ("Mixed", "Intermediate", "Upper Intermediate", "Advanced")
QUESTION_COUNTS = (5, 10, 15, 20)


def _clean(value):
    return str(value or "").strip()


def _level_filter(query, level):
    if not level or str(level).lower() == "mixed":
        return query
    return query.filter(VocabularyMaster.level == normalize_level(level))


def _progress_vocab_query(user_id, level):
    return _level_filter(
        VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment))
        .join(UserWordProgress, UserWordProgress.vocabulary_id == VocabularyMaster.id)
        .filter(UserWordProgress.user_id == user_id),
        level,
    )


def _source_query(user_id, source, level):
    source = source or "mixed_curriculum"
    if source == "learned_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_learned.is_(True))
    if source == "difficult_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_difficult.is_(True))
    if source == "generated_words":
        return _progress_vocab_query(user_id, level).filter(UserWordProgress.is_generated.is_(True))
    if source == "unseen_vocabulary":
        seen = (
            db.session.query(UserWordProgress.vocabulary_id)
            .filter(
                UserWordProgress.user_id == user_id,
                or_(UserWordProgress.is_generated.is_(True), UserWordProgress.is_learned.is_(True)),
            )
            .subquery()
        )
        return _level_filter(
            VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)).filter(~VocabularyMaster.id.in_(seen)),
            level,
        )
    if source == "level_curriculum":
        return _level_filter(VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)), level)
    return _level_filter(VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)), level)


def _search_vocabulary_rows(user_id, count):
    return (
        SearchVocabulary.query.filter_by(searched_by_user_id=user_id)
        .order_by(SearchVocabulary.created_at.desc(), SearchVocabulary.id.desc())
        .limit(count)
        .all()
    )


def _meaning(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.definition if enrichment else "")


def _bangla(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.bangla_meaning if enrichment else "")


def _sentence(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.example_sentence if enrichment else "")


def _synonym(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.synonyms if enrichment else "")


def _antonym(vocabulary):
    enrichment = vocabulary.enrichment
    return _clean(enrichment.antonyms if enrichment else "")


def _distractors(vocabulary, pool, getter, count=3):
    values = []
    seen = {_clean(getter(vocabulary)).lower(), vocabulary.word.lower()}
    for item in pool:
        if item.enrichment is None:
            get_or_create_enrichment(item, allow_ai=False)
        value = _clean(getter(item))
        if getter == _meaning and (not value or value.lower() in seen):
            value = f"A vocabulary meaning for {item.word}."
        if value and value.lower() not in seen:
            seen.add(value.lower())
            values.append(value)
        if len(values) >= count:
            break
    return values


def _options(answer, distractors):
    choices = [answer] + distractors[:3]
    random.shuffle(choices)
    return choices


def _question_for(vocabulary, quiz_type, pool):
    get_or_create_enrichment(vocabulary, allow_ai=True)
    answer_word = vocabulary.word
    meaning = _meaning(vocabulary) or "Definition is being prepared."
    bangla = _bangla(vocabulary)
    sentence = _sentence(vocabulary)
    synonym = _synonym(vocabulary)
    antonym = _antonym(vocabulary)
    quiz_type = quiz_type or "multiple_choice"

    if quiz_type == "fill_blank":
        prompt_sentence = sentence or f"The word {answer_word} belongs in this sentence."
        prompt = prompt_sentence.replace(answer_word, "____", 1)
        if prompt == prompt_sentence:
            prompt = f"Fill in the blank: ____ means {meaning}"
        return {
            "question_type": "fill_blank",
            "subtitle": "Type the missing vocabulary word",
            "prompt": prompt,
            "answer": answer_word,
            "options": [],
        }
    if quiz_type == "reverse_meaning":
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the word that matches this meaning",
            "prompt": meaning,
            "answer": answer_word,
            "options": _options(answer_word, _distractors(vocabulary, pool, lambda item: item.word)),
        }
    if quiz_type == "bangla_to_english" and bangla:
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the English word",
            "prompt": bangla,
            "answer": answer_word,
            "options": _options(answer_word, _distractors(vocabulary, pool, lambda item: item.word)),
        }
    if quiz_type == "english_to_bangla" and bangla:
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the Bangla meaning",
            "prompt": answer_word,
            "answer": bangla,
            "options": _options(bangla, _distractors(vocabulary, pool, _bangla)),
        }
    if quiz_type == "synonym_match" and synonym:
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the closest synonym",
            "prompt": answer_word,
            "answer": synonym,
            "options": _options(synonym, _distractors(vocabulary, pool, _synonym)),
        }
    if quiz_type == "meaning_match":
        return {
            "question_type": "multiple_choice",
            "subtitle": "Choose the correct meaning",
            "prompt": answer_word,
            "answer": meaning,
            "options": _options(meaning, _distractors(vocabulary, pool, _meaning)),
        }
    return {
        "question_type": "multiple_choice",
        "subtitle": "Choose the correct meaning",
        "prompt": answer_word,
        "answer": meaning,
        "options": _options(meaning, _distractors(vocabulary, pool, _meaning)),
    }


def build_curriculum_quiz_questions(
    user_id,
    total_questions=5,
    quiz_type="multiple_choice",
    level="Mixed",
    word_source="mixed_curriculum",
    focus="",
    exclude_vocabulary_ids=None,
    specific_vocabulary_ids=None,
):
    exclude_vocabulary_ids = set(exclude_vocabulary_ids or [])
    total_questions = total_questions if total_questions in QUESTION_COUNTS else 5
    if word_source == "search_vocabulary" and not specific_vocabulary_ids:
        rows = _search_vocabulary_rows(user_id, max(total_questions * 2, 12))
        questions = []
        for row in rows:
            meaning = _clean(row.definition) or "Definition is being prepared."
            bangla = _clean(row.bangla_meaning)
            answer_word = row.word
            if quiz_type == "fill_blank":
                prompt = (_clean(row.example_sentence) or f"____ means {meaning}").replace(answer_word, "____", 1)
                question = {"question_type": "fill_blank", "subtitle": "Type the searched word", "prompt": prompt, "answer": answer_word, "options": []}
            elif quiz_type == "bangla_to_english" and bangla:
                question = {"question_type": "multiple_choice", "subtitle": "Choose the English word", "prompt": bangla, "answer": answer_word, "options": _options(answer_word, [item.word for item in rows if item.id != row.id])}
            elif quiz_type == "english_to_bangla" and bangla:
                question = {"question_type": "multiple_choice", "subtitle": "Choose the Bangla meaning", "prompt": answer_word, "answer": bangla, "options": _options(bangla, [_clean(item.bangla_meaning) for item in rows if item.id != row.id and _clean(item.bangla_meaning)])}
            else:
                question = {"question_type": "multiple_choice", "subtitle": "Choose the correct meaning", "prompt": answer_word, "answer": meaning, "options": _options(meaning, [_clean(item.definition) for item in rows if item.id != row.id and _clean(item.definition)])}
            question.update({"vocabulary_id": None, "user_word_id": None, "word": answer_word, "explanation": meaning})
            if question["question_type"] == "fill_blank" or len(question["options"]) >= 2:
                questions.append(question)
            if len(questions) >= total_questions:
                break
        return questions
    if specific_vocabulary_ids:
        query = VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment)).filter(VocabularyMaster.id.in_(specific_vocabulary_ids))
    else:
        query = _source_query(user_id, word_source, level)
    if exclude_vocabulary_ids:
        query = query.filter(~VocabularyMaster.id.in_(exclude_vocabulary_ids))

    if word_source == "difficult_words" or "difficult" in _clean(focus).lower():
        query = query.order_by(UserWordProgress.is_difficult.desc(), UserWordProgress.last_reviewed_at.asc().nullsfirst(), func.random())
    elif word_source == "unseen_vocabulary":
        query = query.order_by(func.random())
    else:
        query = query.order_by(func.random())

    vocabularies = query.limit(max(total_questions * 2, 12)).all()
    if not vocabularies and word_source != "mixed_curriculum":
        vocabularies = _source_query(user_id, "mixed_curriculum", level).order_by(func.random()).limit(max(total_questions * 2, 12)).all()

    random.shuffle(vocabularies)
    pool = _source_query(user_id, "mixed_curriculum", "Mixed").order_by(func.random()).limit(80).all()
    questions = []
    for vocabulary in vocabularies:
        question = _question_for(vocabulary, quiz_type, pool)
        if question.get("question_type") != "fill_blank" and len(question.get("options", [])) < 2:
            continue
        progress = UserWordProgress.query.filter_by(user_id=user_id, vocabulary_id=vocabulary.id).first()
        question.update(
            {
                "vocabulary_id": vocabulary.id,
                "user_word_id": progress.id if progress else None,
                "word": vocabulary.word,
                "explanation": _meaning(vocabulary),
            }
        )
        questions.append(question)
        if len(questions) >= total_questions:
            break
    return questions


def quiz_started_at():
    return int(datetime.utcnow().timestamp())
