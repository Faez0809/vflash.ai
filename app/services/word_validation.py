import re
from functools import lru_cache

from ai_generator import CURATED_WORD_CONTENT, FALLBACK_VOCABULARY

from app.models import MasterWord, db
from app.services.stats import clean_text, get_vocabulary_suggestions


WORD_PATTERN = re.compile(r"^[a-z]+(?:[a-z'-]*[a-z]+)?$")
PARTS_OF_SPEECH = {"noun", "verb", "adjective", "adverb", "pronoun", "preposition", "conjunction", "interjection"}
TOPIC_STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
TOPIC_EXPANSIONS = {
    "academic": {"education", "essay", "research", "study", "university", "writing"},
    "business": {"company", "corporate", "finance", "management", "market", "office", "workplace"},
    "communication": {"conversation", "language", "message", "presentation", "speaking", "writing"},
    "economy": {"economic", "finance", "income", "market", "policy", "trade"},
    "education": {"academic", "classroom", "exam", "learning", "school", "student", "study", "teacher"},
    "environment": {"climate", "ecology", "energy", "nature", "pollution", "sustainability"},
    "health": {"care", "disease", "fitness", "hospital", "medical", "medicine", "wellness"},
    "ielts": {"academic", "essay", "exam", "speaking", "test", "vocabulary", "writing"},
    "media": {"content", "digital", "journalism", "news", "platform", "social"},
    "personal": {"growth", "habit", "lifestyle", "mindset", "self"},
    "preparation": {"exam", "practice", "readiness", "study", "training"},
    "psychology": {"behavior", "cognitive", "emotion", "mental", "mind"},
    "society": {"community", "culture", "policy", "public", "social"},
    "technology": {"ai", "computer", "data", "digital", "innovation", "internet", "software", "technical"},
    "travel": {"airport", "destination", "hotel", "journey", "tourism", "transport", "trip"},
    "work": {"business", "career", "company", "employee", "job", "office", "professional"},
}
LOW_CONFIDENCE_PREFIXES = (
    "a simple meaning for ",
    "simple meaning for ",
)


def normalize_word(value):
    return clean_text(value).strip().lower()


def normalize_single_word(value):
    normalized = normalize_word(value)
    if not normalized or " " in normalized or not WORD_PATTERN.fullmatch(normalized):
        return ""
    return normalized


@lru_cache(maxsize=1)
def _static_reference_words():
    words = set(CURATED_WORD_CONTENT.keys())
    for items in FALLBACK_VOCABULARY.values():
        words.update(clean_text(item.get("word")).lower() for item in items if clean_text(item.get("word")))
    return {word for word in words if word}


def reference_candidates(include_db_valid=True):
    candidates = set(_static_reference_words())
    candidates.update(
        clean_text(row[0]).lower()
        for row in db.session.query(MasterWord.word).distinct().all()
        if clean_text(row[0])
    )
    return sorted(candidates)


def is_valid_english_word(value):
    normalized = normalize_single_word(value)
    if not normalized:
        return False
    if normalized in _static_reference_words():
        return True
    return db.session.query(MasterWord.id).filter(MasterWord.word == normalized).first() is not None


def find_closest_valid_words(value, limit=3, candidates=None):
    normalized = normalize_single_word(value)
    if not normalized:
        return []
    suggestions = get_vocabulary_suggestions(normalized, candidates or reference_candidates(), limit=limit, cutoff=0.72)
    return [item["word"] for item in suggestions[:limit]]


def _tokenize_topic_text(value):
    tokens = []
    for token in re.findall(r"[a-z]+", normalize_word(value)):
        if len(token) < 3 or token in TOPIC_STOPWORDS:
            continue
        tokens.append(token)
        if token.endswith("s") and len(token) > 4:
            tokens.append(token[:-1])
    return set(tokens)


def _expanded_topic_terms(topic):
    terms = _tokenize_topic_text(topic)
    expanded = set(terms)
    for term in list(terms):
        expanded.update(TOPIC_EXPANSIONS.get(term, set()))
    return expanded


def topic_relevance(topic_hint, payload):
    normalized_topic = clean_text(topic_hint)
    if not normalized_topic:
        return {"is_relevant": True, "score": 1.0, "matched_terms": []}

    haystack = " ".join(
        clean_text((payload or {}).get(field_name))
        for field_name in ("topic", "meaning", "sentence", "memory_trick")
    ).lower()
    if not haystack:
        return {"is_relevant": False, "score": 0.0, "matched_terms": []}

    topic_terms = _expanded_topic_terms(normalized_topic)
    if not topic_terms:
        return {"is_relevant": True, "score": 1.0, "matched_terms": []}

    haystack_terms = _tokenize_topic_text(haystack)
    matched_terms = sorted(topic_terms.intersection(haystack_terms))
    phrase_match = normalize_word(normalized_topic) in haystack
    score = 1.0 if phrase_match else (len(matched_terms) / max(1, min(len(topic_terms), 4)))
    return {
        "is_relevant": phrase_match or bool(matched_terms),
        "score": round(score, 3),
        "matched_terms": matched_terms,
    }


def has_consistent_meaning(word_text, payload):
    normalized_word = normalize_single_word(word_text)
    meaning = clean_text((payload or {}).get("meaning")).lower()
    sentence = clean_text((payload or {}).get("sentence")).lower()
    part_of_speech = clean_text((payload or {}).get("part_of_speech")).lower()

    if not normalized_word or not meaning:
        return False
    if meaning == normalized_word:
        return False
    if any(meaning.startswith(prefix + normalized_word) for prefix in LOW_CONFIDENCE_PREFIXES):
        return False
    if meaning.startswith(f"{normalized_word} is "):
        return False
    if sentence and sentence == f"i used the word {normalized_word} in a simple sentence.":
        return False
    if part_of_speech and part_of_speech not in PARTS_OF_SPEECH:
        return False
    return True


def validate_word_payload(word_text, payload=None, topic_hint=""):
    normalized_word = normalize_single_word(word_text)
    if not normalized_word:
        return {
            "normalized_word": "",
            "is_valid": False,
            "reason": "invalid_format",
            "spelling_valid": False,
            "meaning_valid": False,
            "topic_valid": not bool(clean_text(topic_hint)),
            "suggestions": [],
        }

    spelling_valid = is_valid_english_word(normalized_word)
    meaning_valid = has_consistent_meaning(normalized_word, payload or {})
    topic_check = topic_relevance(topic_hint, payload or {})
    topic_valid = topic_check["is_relevant"]

    reason = ""
    if not spelling_valid:
        reason = "invalid_spelling"
    elif payload is not None and not meaning_valid:
        reason = "meaning_mismatch"
    elif clean_text(topic_hint) and not topic_valid:
        reason = "topic_mismatch"

    return {
        "normalized_word": normalized_word,
        "is_valid": spelling_valid and (payload is None or meaning_valid) and (not clean_text(topic_hint) or topic_valid),
        "reason": reason,
        "spelling_valid": spelling_valid,
        "meaning_valid": meaning_valid,
        "topic_valid": topic_valid,
        "topic_score": topic_check["score"],
        "matched_topic_terms": topic_check["matched_terms"],
        "suggestions": [] if spelling_valid else find_closest_valid_words(normalized_word),
    }


def validate_word_model(word, topic_hint=""):
    if word is None:
        return {
            "normalized_word": "",
            "is_valid": False,
            "reason": "missing_word",
            "suggestions": [],
        }
    return validate_word_payload(
        getattr(word, "word", ""),
        payload={
            "part_of_speech": getattr(word, "part_of_speech", ""),
            "meaning": getattr(word, "meaning", ""),
            "sentence": getattr(word, "sentence", ""),
            "memory_trick": getattr(word, "memory_trick", ""),
            "topic": getattr(word, "topic", ""),
        },
        topic_hint=topic_hint or clean_text(getattr(word, "topic", "")),
    )


def mark_word_invalid(word):
    if word is None:
        return False
    if getattr(word, "is_valid", True) is False:
        return False
    word.is_valid = False
    return True
