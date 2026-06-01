from datetime import date
import re
from types import SimpleNamespace

from ai_generator import CURATED_WORD_CONTENT, FALLBACK_RELATIONS, FALLBACK_VOCABULARY
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app import cache
from app.models import StudySession, UserWord, Word, db
from app.services.ai_generator import generate_word_content, generate_word_details, retry_generate_word_details, suggest_word_corrections
from app.services.stats import clean_text, get_vocabulary_suggestions, suggest_vocabulary_correction
from app.services.word_validation import (
    is_valid_english_word,
    mark_word_invalid,
    reference_candidates,
    validate_word_payload,
)


FALLBACK_CONTINUE_MESSAGE = (
    "New content is being prepared. For now, we've loaded words from your existing collection "
    "so you can continue learning without interruption."
)


def invalidate_word_list_cache():
    # Refresh the shared search dictionary after word inserts.
    cache.delete("search:candidate_words:v1")


def _invalidate_stored_word_if_needed(normalized_word):
    stored_word = Word.query.filter_by(word=normalized_word).first()
    if stored_word is None:
        return None

    validation = validate_word_payload(
        normalized_word,
        payload={
            "part_of_speech": getattr(stored_word, "part_of_speech", ""),
            "meaning": getattr(stored_word, "meaning", ""),
            "sentence": getattr(stored_word, "sentence", ""),
            "memory_trick": getattr(stored_word, "memory_trick", ""),
            "topic": getattr(stored_word, "topic", ""),
        },
    )
    if validation["is_valid"]:
        if stored_word.is_valid is False:
            stored_word.is_valid = True
            db.session.commit()
            invalidate_word_list_cache()
        return stored_word

    if mark_word_invalid(stored_word):
        db.session.commit()
        invalidate_word_list_cache()
    return None


def _fallback_vocabulary_index():
    indexed = {}
    for level_items in FALLBACK_VOCABULARY.values():
        for item in level_items:
            normalized_word = clean_text(item.get("word")).lower()
            if normalized_word and normalized_word not in indexed:
                indexed[normalized_word] = dict(item)
    return indexed


FALLBACK_VOCABULARY_INDEX = _fallback_vocabulary_index()


def _clean_relation_candidate(value, normalized_word, allow_phrase=False):
    cleaned = clean_text(value).lower()
    if not cleaned:
        return None
    if cleaned == clean_text(normalized_word).lower():
        return None
    if len(cleaned.split()) > (3 if allow_phrase else 2):
        return None
    if not re.fullmatch(r"[a-z][a-z\s'\-]*[a-z]", cleaned):
        return None
    return cleaned


def _curated_word_payload(normalized_word):
    curated = CURATED_WORD_CONTENT.get(normalized_word)
    if not curated:
        return None

    payload = dict(curated)
    payload["word"] = normalized_word
    payload["topic"] = clean_text(payload.get("topic")) or "general"
    payload["synonym"] = _clean_relation_candidate(payload.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(FALLBACK_RELATIONS.get(normalized_word, {}).get("synonym"), normalized_word, allow_phrase=True) or None
    payload["antonym"] = _clean_relation_candidate(payload.get("antonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(FALLBACK_RELATIONS.get(normalized_word, {}).get("antonym"), normalized_word, allow_phrase=True) or None
    return payload


def _lookup_candidates(normalized_word):
    candidates = []

    def add(value):
        value = clean_text(value).lower()
        if len(value) < 3 or value in candidates:
            return
        candidates.append(value)

    add(normalized_word)

    if normalized_word.endswith("ied") and len(normalized_word) > 4:
        add(normalized_word[:-3] + "y")
    if normalized_word.endswith("ed") and len(normalized_word) > 4:
        stem = normalized_word[:-2]
        add(stem)
        add(normalized_word[:-1])
        if not stem.endswith("e"):
            add(stem + "e")
        if len(stem) > 2 and stem[-1] == stem[-2]:
            add(stem[:-1])
    if normalized_word.endswith("ing") and len(normalized_word) > 5:
        stem = normalized_word[:-3]
        add(stem)
        add(stem + "e")
        if len(stem) > 2 and stem[-1] == stem[-2]:
            add(stem[:-1])
    if normalized_word.endswith("es") and len(normalized_word) > 4:
        add(normalized_word[:-2])
        add(normalized_word[:-1])
    if normalized_word.endswith("s") and len(normalized_word) > 3:
        add(normalized_word[:-1])
    if normalized_word.endswith("ly") and len(normalized_word) > 4:
        add(normalized_word[:-2])

    return candidates


def _best_generated_payload(normalized_word, allow_variants=False):
    candidates = _lookup_candidates(normalized_word) if allow_variants else [normalized_word]
    for candidate in candidates:
        curated_payload = _curated_word_payload(candidate)
        if curated_payload:
            return dict(curated_payload)

        candidate_word = Word.query.filter_by(word=candidate, is_valid=True).first()
        if candidate_word is not None:
            payload = _word_payload_from_model(candidate_word)
            if not is_low_confidence_word_payload(payload, candidate):
                payload["word"] = candidate
                payload["synonym"] = _clean_relation_candidate(payload.get("synonym"), candidate, allow_phrase=True) or _clean_relation_candidate(FALLBACK_RELATIONS.get(candidate, {}).get("synonym"), candidate, allow_phrase=True) or None
                payload["antonym"] = _clean_relation_candidate(FALLBACK_RELATIONS.get(candidate, {}).get("antonym"), candidate, allow_phrase=True) or None
                return payload

        generated = generate_word_content(candidate)
        if not is_low_confidence_word_payload(generated, candidate):
            payload = dict(generated)
            payload["word"] = candidate
            payload["topic"] = clean_text(payload.get("topic")) or "general"
            return payload

    return None


def _word_payload_from_model(word):
    return {
        "word": clean_text(getattr(word, "word", "")).lower(),
        "part_of_speech": clean_text(getattr(word, "part_of_speech", "")) or None,
        "meaning": clean_text(getattr(word, "meaning", "")),
        "bangla_meaning": clean_text(getattr(word, "bangla_meaning", "")) or None,
        "phonetic": clean_text(getattr(word, "phonetic", "")) or None,
        "synonym": clean_text(getattr(word, "synonym", "")) or None,
        "sentence": clean_text(getattr(word, "sentence", "")) or None,
        "memory_trick": clean_text(getattr(word, "memory_trick", "")) or None,
        "topic": clean_text(getattr(word, "topic", "")) or "general",
    }


def is_low_confidence_word_payload(payload, normalized_word):
    if not payload:
        return True

    normalized_word = clean_text(normalized_word).lower()
    meaning = clean_text(payload.get("meaning")).lower()
    bangla_meaning = clean_text(payload.get("bangla_meaning")).lower()
    sentence = clean_text(payload.get("sentence")).lower()
    phonetic = clean_text(payload.get("phonetic")).lower()
    synonym = clean_text(payload.get("synonym")).lower()
    memory_trick = clean_text(payload.get("memory_trick")).lower()

    generic_meaning = (
        not meaning
        or meaning == normalized_word
        or "simple meaning for" in meaning
        or meaning.startswith(f"{normalized_word} is ")
    )
    generic_bangla = (
        not bangla_meaning
        or "সহজ বাংলা অর্থ" in bangla_meaning
        or bangla_meaning.startswith(f"{normalized_word} ")
    )
    generic_bangla = generic_bangla or "সহজ বাংলা অর্থ" in bangla_meaning
    generic_bangla = generic_bangla or ("বাংলা অর্থ" in bangla_meaning and normalized_word in bangla_meaning)
    generic_sentence = (
        not sentence
        or sentence == f"i used the word {normalized_word} in a simple sentence."
        or sentence.startswith("i used the word ")
    )
    generic_memory = (
        not memory_trick
        or memory_trick.startswith("think of the sound of ")
        or "connect it with a daily example" in memory_trick
    )
    weak_pronunciation = not phonetic or phonetic == normalized_word
    weak_synonym = not synonym or synonym == normalized_word

    suspicious_markers = sum(
        [
            generic_bangla,
            generic_sentence,
            generic_memory,
            weak_pronunciation,
            weak_synonym,
        ]
    )
    return generic_meaning or suspicious_markers >= 3


def _build_transient_word_payload(normalized_word):
    relations = FALLBACK_RELATIONS.get(normalized_word, {})
    return {
        "word": normalized_word,
        "part_of_speech": None,
        "meaning": "Loading a complete word profile.",
        "bangla_meaning": None,
        "phonetic": None,
        "synonym": _clean_relation_candidate(relations.get("synonym"), normalized_word, allow_phrase=True) or None,
        "antonym": _clean_relation_candidate(relations.get("antonym"), normalized_word, allow_phrase=True) or None,
        "memory_trick": None,
        "topic": "general",
        "sentence": None,
        "lookup_pending": True,
    }


def _payload_to_word_stub(payload):
    data = {
        "id": None,
        "word": clean_text(payload.get("word")).lower(),
        "part_of_speech": clean_text(payload.get("part_of_speech")) or None,
        "meaning": clean_text(payload.get("meaning")),
        "bangla_meaning": clean_text(payload.get("bangla_meaning")) or None,
        "phonetic": clean_text(payload.get("phonetic")) or None,
        "synonym": _clean_relation_candidate(payload.get("synonym"), clean_text(payload.get("word")).lower(), allow_phrase=True) or None,
        "memory_trick": clean_text(payload.get("memory_trick")) or None,
        "topic": clean_text(payload.get("topic")) or "general",
        "sentence": clean_text(payload.get("sentence")) or None,
        "created_at": None,
        "synonym_hint": _clean_relation_candidate(payload.get("synonym"), clean_text(payload.get("word")).lower(), allow_phrase=True) or None,
        "antonym_hint": _clean_relation_candidate(payload.get("antonym"), clean_text(payload.get("word")).lower(), allow_phrase=True) or None,
        "lookup_pending": bool(payload.get("lookup_pending")),
    }
    return SimpleNamespace(**data)


def _normalize_dictionary_details(query, result):
    normalized_query = clean_text(query).lower()
    payload = dict(result or {})
    status = clean_text(payload.get("status")).lower() or "ok"
    returned_word = clean_text(payload.get("word")).lower() or normalized_query
    synonyms = payload.get("synonyms")
    if not isinstance(synonyms, list):
        synonyms = []

    cleaned_synonyms = []
    seen = set()
    for item in synonyms:
        cleaned = _clean_relation_candidate(item, returned_word, allow_phrase=True)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_synonyms.append(cleaned)

    difficulty = clean_text(payload.get("difficulty")).lower()
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list):
        suggestions = []

    cleaned_suggestions = []
    suggestion_seen = set()
    for item in suggestions:
        cleaned = clean_text(item).lower()
        if not cleaned or cleaned == normalized_query or cleaned in suggestion_seen:
            continue
        suggestion_seen.add(cleaned)
        cleaned_suggestions.append(cleaned)

    pronunciation = _normalize_readable_pronunciation(payload.get("pronunciation") or payload.get("phonetic"), returned_word)
    memory_trick = clean_text(payload.get("memory_trick"))
    if len(memory_trick) <= 5:
        memory_trick = _fallback_memory_trick(clean_text(payload.get("meaning")))

    return {
        "status": status,
        "word": returned_word,
        "part_of_speech": clean_text(payload.get("part_of_speech")) or None,
        "meaning": clean_text(payload.get("meaning")),
        "sentence": clean_text(payload.get("sentence")) or None,
        "synonyms": cleaned_synonyms,
        "synonym": cleaned_synonyms[0] if cleaned_synonyms else None,
        "phonetic": pronunciation,
        "bangla_meaning": clean_text(payload.get("bangla_meaning")) or None,
        "memory_trick": memory_trick or None,
        "difficulty": difficulty,
        "suggestions": cleaned_suggestions,
        "topic": "general",
        "lookup_pending": False,
    }


def _fallback_memory_trick(meaning):
    cleaned_meaning = clean_text(meaning)
    if not cleaned_meaning:
        return None
    return f"Associate this word with: {cleaned_meaning}"


def _normalize_readable_pronunciation(value, word):
    cleaned = clean_text(value).lower()
    cleaned = re.sub(r"[\/\[\]\(\)ˈˌː.]", "", cleaned)
    cleaned = re.sub(r"[^a-z\s\-]", "", cleaned)
    cleaned = re.sub(r"\s+", "-", cleaned).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    if len(cleaned) > 3 and "-" in cleaned:
        return cleaned
    return _approximate_readable_pronunciation(word)


def _approximate_readable_pronunciation(word):
    cleaned_word = re.sub(r"[^a-z]", "", clean_text(word).lower())
    if len(cleaned_word) <= 3:
        return cleaned_word or None

    vowels = "aeiouy"
    syllables = []
    current = ""
    for index, char in enumerate(cleaned_word):
        current += char
        next_char = cleaned_word[index + 1] if index + 1 < len(cleaned_word) else ""
        prev_char = cleaned_word[index - 1] if index > 0 else ""
        if char in vowels:
            should_split = (
                not next_char
                or next_char not in vowels
                and any(letter in vowels for letter in cleaned_word[index + 1 :])
                and prev_char != next_char
            )
            if should_split:
                syllables.append(current)
                current = ""
    if current:
        syllables.append(current)

    if not syllables:
        syllables = [cleaned_word]
    return "-".join(part for part in syllables if part)


def _sentence_uses_word(sentence, word):
    sentence_text = clean_text(sentence).lower()
    normalized_word = clean_text(word).lower()
    if not sentence_text or not normalized_word:
        return False
    if " " in normalized_word:
        return normalized_word in sentence_text
    return re.search(rf"\b{re.escape(normalized_word)}\b", sentence_text) is not None


def _is_verified_dictionary_result(query, result):
    normalized_query = clean_text(query).lower()
    if not normalized_query:
        return False
    if clean_text(result.get("status")).lower() == "invalid":
        return False
    if clean_text(result.get("word")).lower() != normalized_query:
        return False
    if len(clean_text(result.get("meaning"))) <= 10:
        return False
    if not clean_text(result.get("part_of_speech")):
        return False
    if not result.get("synonyms"):
        return False
    pronunciation = clean_text(result.get("phonetic"))
    if len(pronunciation) <= 3:
        return False
    if re.search(r"[\/\[\]\(\)ˈˌː]", pronunciation):
        return False
    if not clean_text(result.get("bangla_meaning")):
        return False
    if len(clean_text(result.get("memory_trick"))) <= 5:
        return False
    if not _sentence_uses_word(result.get("sentence"), normalized_query):
        return False
    return True


def _request_dictionary_result(normalized_word, retry=False):
    response = retry_generate_word_details(normalized_word) if retry else generate_word_details(normalized_word)
    print("AI raw response:", response)
    return _normalize_dictionary_details(normalized_word, response)


def _save_verified_dictionary_result(result):
    normalized_word = clean_text(result.get("word")).lower()
    if not normalized_word:
        return None

    word = Word.query.filter_by(word=normalized_word).first()
    if word is None:
        word = Word(word=normalized_word)
        db.session.add(word)

    word.meaning = clean_text(result.get("meaning"))
    word.part_of_speech = clean_text(result.get("part_of_speech")) or None
    word.sentence = clean_text(result.get("sentence")) or None
    joined_synonyms = ", ".join(result.get("synonyms", []))
    word.synonym = clean_text(joined_synonyms) or _clean_relation_candidate(result.get("synonym"), normalized_word, allow_phrase=True) or None
    word.phonetic = clean_text(result.get("phonetic")) or None
    word.bangla_meaning = clean_text(result.get("bangla_meaning")) or None
    word.memory_trick = clean_text(result.get("memory_trick")) or None
    word.topic = "general"
    word.difficulty = clean_text(result.get("difficulty")).lower() or "medium"
    word.is_valid = True
    if not getattr(word, "created_at", None):
        word.created_at = date.today()

    db.session.commit()
    invalidate_word_list_cache()
    enrich_word_collection([word], allow_ai=False)
    return word


def get_reference_vocabulary_candidates():
    return reference_candidates()


def is_known_dictionary_word(normalized_word):
    return is_valid_english_word(normalized_word)


def find_related_word_forms(normalized_word, preferred_part_of_speech=None, limit=4):
    normalized_word = clean_text(normalized_word).lower()
    if not normalized_word or len(normalized_word) < 3:
        return []

    candidates = {}

    def add_candidate(word_text, part_of_speech=None):
        cleaned_word = clean_text(word_text).lower()
        if (
            not cleaned_word
            or cleaned_word == normalized_word
            or len(cleaned_word) - len(normalized_word) > 6
            or normalized_word not in cleaned_word
        ):
            return
        candidates[cleaned_word] = clean_text(part_of_speech).lower() or candidates.get(cleaned_word)

    for row in (
        db.session.query(Word.word, Word.part_of_speech)
        .filter(Word.word != normalized_word, Word.is_valid.is_(True))
        .filter((Word.word.ilike(f"{normalized_word}%")) | (Word.word.ilike(f"%{normalized_word}")))
        .limit(16)
        .all()
    ):
        add_candidate(row[0], row[1])

    for word_text, payload in CURATED_WORD_CONTENT.items():
        add_candidate(word_text, payload.get("part_of_speech"))

    for word_text, payload in FALLBACK_VOCABULARY_INDEX.items():
        add_candidate(word_text, payload.get("part_of_speech"))

    ranked = sorted(
        candidates.items(),
        key=lambda item: (
            0 if preferred_part_of_speech and item[1] == preferred_part_of_speech else 1,
            abs(len(item[0]) - len(normalized_word)),
            item[0],
        ),
    )
    return [word for word, _ in ranked[:limit]]


def resolve_vocabulary_lookup(raw_word, preferred_part_of_speech=None, correction_candidates=None):
    normalized_word = clean_text(raw_word).lower()
    if not normalized_word:
        return {
            "searched_word": "",
            "resolved_word": "",
            "word": None,
            "status": "empty",
            "autocorrected_from": None,
            "suggestions": [],
            "related_words": [],
        }

    print("Query:", normalized_word)

    word = Word.query.filter_by(word=normalized_word, is_valid=True).first()
    if word is not None:
        existing_result = _normalize_dictionary_details(
            normalized_word,
            {
                "status": "ok",
                "word": getattr(word, "word", normalized_word),
                "part_of_speech": getattr(word, "part_of_speech", None),
                "meaning": getattr(word, "meaning", ""),
                "sentence": getattr(word, "sentence", None),
                "synonyms": [item.strip() for item in clean_text(getattr(word, "synonym", "")).split(",") if item.strip()],
                "pronunciation": getattr(word, "phonetic", None),
                "bangla_meaning": getattr(word, "bangla_meaning", None),
                "memory_trick": getattr(word, "memory_trick", None),
                "difficulty": getattr(word, "difficulty", None),
            },
        )
        if _is_verified_dictionary_result(normalized_word, existing_result):
            enrich_word_collection([word], allow_ai=False)
            return {
                "searched_word": normalized_word,
                "resolved_word": normalized_word,
                "word": word,
                "status": "exact",
                "autocorrected_from": None,
                "suggestions": [],
                "related_words": find_related_word_forms(normalized_word, preferred_part_of_speech=preferred_part_of_speech),
            }

        word.is_valid = False
        db.session.commit()
        invalidate_word_list_cache()

    if word is not None:
        word = None

    try:
        result = _request_dictionary_result(normalized_word, retry=False)
    except Exception:
        result = None
        print("AI raw response:", result)

    if result:
        validation_passed = _is_verified_dictionary_result(normalized_word, result)
        print("Validation passed:", validation_passed)
        if result.get("status") == "invalid":
            return {
                "searched_word": normalized_word,
                "resolved_word": normalized_word,
                "word": None,
                "status": "error",
                "autocorrected_from": None,
                "suggestions": result.get("suggestions", []),
                "related_words": [],
            }

        if validation_passed:
            saved_word = _save_verified_dictionary_result(result)
            if saved_word is not None:
                print("Saved to DB:", result["word"])
                return {
                    "searched_word": normalized_word,
                    "resolved_word": normalized_word,
                    "word": saved_word,
                    "status": "exact",
                    "autocorrected_from": None,
                    "suggestions": [],
                    "related_words": find_related_word_forms(normalized_word, preferred_part_of_speech=preferred_part_of_speech),
                }

    try:
        retry_result = _request_dictionary_result(normalized_word, retry=True)
    except Exception:
        retry_result = None
        print("AI raw response:", retry_result)

    if retry_result:
        retry_validation_passed = _is_verified_dictionary_result(normalized_word, retry_result)
        print("Validation passed:", retry_validation_passed)
        if retry_result.get("status") == "invalid":
            return {
                "searched_word": normalized_word,
                "resolved_word": normalized_word,
                "word": None,
                "status": "error",
                "autocorrected_from": None,
                "suggestions": retry_result.get("suggestions", []),
                "related_words": [],
            }
        if retry_validation_passed:
            saved_word = _save_verified_dictionary_result(retry_result)
            if saved_word is not None:
                print("Saved to DB:", retry_result["word"])
                return {
                    "searched_word": normalized_word,
                    "resolved_word": normalized_word,
                    "word": saved_word,
                    "status": "exact",
                    "autocorrected_from": None,
                    "suggestions": [],
                    "related_words": find_related_word_forms(normalized_word, preferred_part_of_speech=preferred_part_of_speech),
                }

        transient_word = _payload_to_word_stub(retry_result)
        return {
            "searched_word": normalized_word,
            "resolved_word": normalized_word,
            "word": transient_word,
            "status": "temporary",
            "autocorrected_from": None,
            "suggestions": [],
            "related_words": find_related_word_forms(normalized_word, preferred_part_of_speech=preferred_part_of_speech),
        }

    suggestions = [item for item in suggest_word_corrections(normalized_word, max_suggestions=3) if is_valid_english_word(item)]
    return {
        "searched_word": normalized_word,
        "resolved_word": normalized_word,
        "word": None,
        "status": "error",
        "autocorrected_from": None,
        "suggestions": suggestions,
        "related_words": [],
    }


def apply_word_payload(word, payload, replace_existing=False):
    if word is None or not payload:
        return False

    changed = False
    field_names = [
        "part_of_speech",
        "meaning",
        "bangla_meaning",
        "phonetic",
        "synonym",
        "memory_trick",
        "bangla_pronunciation",
        "topic",
        "sentence",
    ]

    for field_name in field_names:
        field_value = clean_text(payload.get(field_name)) or None
        if not field_value:
            continue
        current_value = clean_text(getattr(word, field_name, "")) or None
        if replace_existing:
            if current_value != field_value:
                setattr(word, field_name, field_value)
                changed = True
        elif not current_value:
            setattr(word, field_name, field_value)
            changed = True

    if not getattr(word, "created_at", None):
        word.created_at = date.today()
        changed = True
    return changed


def touch_user_word_interaction(user_word, interaction_day=None):
    if user_word is None:
        return False
    interaction_day = interaction_day or date.today()
    if user_word.last_reviewed == interaction_day:
        return False
    user_word.last_reviewed = interaction_day
    return True


def upsert_word_from_payload(item, fallback_topic="Vocabulary", fallback_difficulty="Intermediate"):
    normalized_word = clean_text(item.get("word")).lower()
    if not normalized_word:
        return None

    validation = validate_word_payload(
        normalized_word,
        payload={
            "part_of_speech": item.get("part_of_speech"),
            "meaning": item.get("meaning"),
            "sentence": item.get("sentence"),
            "memory_trick": item.get("memory_trick"),
            "topic": clean_text(item.get("topic")) or fallback_topic,
        },
        topic_hint=clean_text(item.get("topic")) or fallback_topic,
    )
    existing_word = Word.query.filter_by(word=normalized_word).first()
    if validation["reason"] == "invalid_format":
        if existing_word is not None and mark_word_invalid(existing_word):
            invalidate_word_list_cache()
        return None

    word = existing_word
    curated_payload = _curated_word_payload(normalized_word) or {}
    relations = FALLBACK_RELATIONS.get(normalized_word, {})
    payload = {
        "part_of_speech": clean_text(curated_payload.get("part_of_speech")) or clean_text(item.get("part_of_speech")) or None,
        "meaning": clean_text(curated_payload.get("meaning")) or clean_text(item.get("meaning")) or f"A simple meaning for {normalized_word}.",
        "bangla_meaning": clean_text(curated_payload.get("bangla_meaning")) or clean_text(item.get("bangla_meaning")) or None,
        "bangla_pronunciation": clean_text(item.get("bangla_pronunciation")) or None,
        "phonetic": clean_text(curated_payload.get("phonetic")) or clean_text(item.get("phonetic")) or None,
        "synonym": _clean_relation_candidate(curated_payload.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(item.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(relations.get("synonym"), normalized_word, allow_phrase=True) or None,
        "memory_trick": clean_text(curated_payload.get("memory_trick")) or clean_text(item.get("memory_trick")) or None,
        "difficulty": clean_text(item.get("difficulty")) or fallback_difficulty,
        "topic": clean_text(curated_payload.get("topic")) or clean_text(item.get("topic")) or fallback_topic,
        "sentence": clean_text(curated_payload.get("sentence")) or clean_text(item.get("sentence")) or None,
        "created_at": date.today(),
        "is_valid": True,
    }

    if word is None:
        word = Word(word=normalized_word, **payload)
        db.session.add(word)
        db.session.flush()
        setattr(word, "synonym_hint", _clean_relation_candidate(curated_payload.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(payload.get("synonym"), normalized_word, allow_phrase=True) or None)
        setattr(word, "antonym_hint", _clean_relation_candidate(curated_payload.get("antonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(relations.get("antonym"), normalized_word, allow_phrase=True) or None)
        setattr(word, "lookup_pending", False)
        return word

    replace_existing = bool(curated_payload) or is_low_confidence_word_payload(_word_payload_from_model(word), normalized_word)

    for field_name, field_value in payload.items():
        current_value = getattr(word, field_name)
        if replace_existing:
            if field_value not in (None, "") and current_value != field_value:
                setattr(word, field_name, field_value)
            continue
        if current_value in (None, "") and field_value not in (None, ""):
            setattr(word, field_name, field_value)
    if not word.created_at:
        word.created_at = date.today()
    word.is_valid = True
    setattr(word, "synonym_hint", _clean_relation_candidate(curated_payload.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(payload.get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(relations.get("synonym"), normalized_word, allow_phrase=True) or None)
    setattr(word, "antonym_hint", _clean_relation_candidate(curated_payload.get("antonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(relations.get("antonym"), normalized_word, allow_phrase=True) or None)
    setattr(word, "lookup_pending", False)
    return word


def find_cached_study_session(user_id, difficulty, word_count, custom_prompt=""):
    normalized_prompt = clean_text(custom_prompt).lower()
    recent_sessions = (
        StudySession.query.filter_by(user_id=user_id, difficulty=difficulty)
        .order_by(StudySession.id.desc())
        .limit(12)
        .all()
    )
    if not recent_sessions:
        return None

    remaining_counts = dict(
        db.session.query(UserWord.session_id, func.count(UserWord.id))
        .filter(
            UserWord.user_id == user_id,
            UserWord.learned.is_(False),
            UserWord.session_id.in_([study_session.id for study_session in recent_sessions]),
        )
        .group_by(UserWord.session_id)
        .all()
    )

    for study_session in recent_sessions:
        session_prompt = clean_text(study_session.custom_prompt).lower()
        if session_prompt != normalized_prompt:
            continue

        remaining_count = remaining_counts.get(study_session.id, 0)
        if remaining_count >= word_count:
            return study_session

    return None


def get_existing_collection_words(user_id, limit=10, difficulty=None, topic_hint=""):
    query = UserWord.query.options(selectinload(UserWord.word_entry)).filter_by(user_id=user_id).join(Word)
    query = query.filter(Word.is_valid.is_(True))

    if difficulty and difficulty != "All":
        query = query.filter(Word.difficulty == difficulty)

    normalized_topic = clean_text(topic_hint).lower()
    if normalized_topic:
        topic_matches = (
            query.filter(Word.topic.isnot(None))
            .filter(Word.topic.ilike(f"%{normalized_topic}%"))
            .order_by(UserWord.is_difficult.desc(), UserWord.learned.asc(), UserWord.added_date.desc(), Word.word.asc())
            .limit(limit)
            .all()
        )
        if topic_matches:
            return topic_matches

    candidates = (
        query.order_by(UserWord.is_difficult.desc(), UserWord.learned.asc(), UserWord.added_date.desc(), Word.word.asc())
        .limit(limit)
        .all()
    )
    return candidates


def enrich_word_support(word, allow_ai=False):
    if word is None:
        return False

    normalized_word = clean_text(getattr(word, "word", "")).lower()
    if not normalized_word:
        return False

    curated_payload = _curated_word_payload(normalized_word)
    if curated_payload:
        changed = apply_word_payload(word, curated_payload, replace_existing=True)
        setattr(word, "synonym_hint", _clean_relation_candidate(curated_payload.get("synonym"), normalized_word, allow_phrase=True) or None)
        setattr(word, "antonym_hint", _clean_relation_candidate(curated_payload.get("antonym"), normalized_word, allow_phrase=True) or None)
        setattr(word, "lookup_pending", False)
        return changed

    relations = FALLBACK_RELATIONS.get(normalized_word, {})
    generated = None
    should_generate = allow_ai and (
        not clean_text(getattr(word, "synonym", ""))
        or not clean_text(getattr(word, "bangla_meaning", ""))
        or not clean_text(getattr(word, "phonetic", ""))
        or not clean_text(getattr(word, "sentence", ""))
        or not clean_text(getattr(word, "memory_trick", ""))
        or is_low_confidence_word_payload(_word_payload_from_model(word), normalized_word)
    )
    if should_generate:
        generated = _best_generated_payload(normalized_word)

    changed = False

    def fill_missing(field_name, *values):
        nonlocal changed
        if clean_text(getattr(word, field_name, "")):
            return
        for value in values:
            cleaned_value = clean_text(value)
            if cleaned_value:
                setattr(word, field_name, cleaned_value)
                changed = True
                return

    if generated:
        changed = apply_word_payload(
            word,
            generated,
            replace_existing=is_low_confidence_word_payload(_word_payload_from_model(word), normalized_word),
        ) or changed

    fill_missing("synonym", (generated or {}).get("synonym"), relations.get("synonym"))
    fill_missing("bangla_meaning", (generated or {}).get("bangla_meaning"))
    fill_missing("phonetic", (generated or {}).get("phonetic"))
    fill_missing("sentence", (generated or {}).get("sentence"))
    fill_missing("memory_trick", (generated or {}).get("memory_trick"))
    fill_missing("topic", (generated or {}).get("topic"))
    fill_missing("part_of_speech", (generated or {}).get("part_of_speech"))

    synonym_hint = _clean_relation_candidate(getattr(word, "synonym", ""), normalized_word, allow_phrase=True) or _clean_relation_candidate((generated or {}).get("synonym"), normalized_word, allow_phrase=True) or _clean_relation_candidate(relations.get("synonym"), normalized_word, allow_phrase=True)
    antonym_hint = _clean_relation_candidate(relations.get("antonym"), normalized_word, allow_phrase=True)

    setattr(word, "synonym_hint", synonym_hint or None)
    setattr(word, "antonym_hint", antonym_hint or None)
    setattr(word, "lookup_pending", False)
    return changed


def enrich_word_collection(words, allow_ai=False):
    changed = False
    seen_ids = set()

    for word in words or []:
        if word is None:
            continue
        word_id = getattr(word, "id", None)
        if word_id in seen_ids:
            continue
        if word_id is not None:
            seen_ids.add(word_id)
        changed = enrich_word_support(word, allow_ai=allow_ai) or changed

    if changed:
        db.session.commit()
    return words


def enrich_user_word_entries(user_words, allow_ai=False):
    enrich_word_collection(
        [item.word_entry for item in (user_words or []) if getattr(item, "word_entry", None) is not None],
        allow_ai=allow_ai,
    )
    return user_words


def get_or_create_word_lookup(raw_word, allow_unverified_generation=False):
    normalized_word = clean_text(raw_word).lower()
    if not normalized_word:
        return None

    curated_payload = _curated_word_payload(normalized_word)
    _invalidate_stored_word_if_needed(normalized_word)
    word = Word.query.filter_by(word=normalized_word, is_valid=True).first()
    if word is not None:
        if curated_payload:
            apply_word_payload(word, curated_payload, replace_existing=True)
            word.is_valid = True
            db.session.commit()
            enrich_word_collection([word], allow_ai=False)
            return word

        existing_payload = _word_payload_from_model(word)
        if is_low_confidence_word_payload(existing_payload, normalized_word):
            refreshed_payload = _best_generated_payload(normalized_word)
            if refreshed_payload:
                apply_word_payload(word, refreshed_payload, replace_existing=True)
                db.session.commit()
            else:
                return _payload_to_word_stub(_build_transient_word_payload(normalized_word))

        enrich_word_collection([word], allow_ai=True)
        return word

    if curated_payload:
        word = Word(
            word=normalized_word,
            is_valid=True,
            part_of_speech=clean_text(curated_payload.get("part_of_speech")) or None,
            meaning=clean_text(curated_payload.get("meaning")) or f"A simple meaning for {normalized_word}.",
            bangla_meaning=clean_text(curated_payload.get("bangla_meaning")) or None,
            phonetic=clean_text(curated_payload.get("phonetic")) or None,
            synonym=_clean_relation_candidate(curated_payload.get("synonym"), normalized_word, allow_phrase=True) or None,
            memory_trick=clean_text(curated_payload.get("memory_trick")) or None,
            topic=clean_text(curated_payload.get("topic")) or "general",
            sentence=clean_text(curated_payload.get("sentence")) or None,
            created_at=date.today(),
        )
        db.session.add(word)
        db.session.commit()
        invalidate_word_list_cache()
        enrich_word_collection([word], allow_ai=False)
        return word

    if not is_known_dictionary_word(normalized_word):
        return None

    content = _best_generated_payload(normalized_word, allow_variants=False)

    if not content:
        return _payload_to_word_stub(_build_transient_word_payload(normalized_word))

    generated_validation = validate_word_payload(
        normalized_word,
        payload=content,
        topic_hint=clean_text(content.get("topic")),
    )
    if not generated_validation["is_valid"]:
        return None

    word = Word(
        word=normalized_word,
        is_valid=True,
        part_of_speech=clean_text(content.get("part_of_speech")) or None,
        meaning=clean_text(content.get("meaning")) or f"A simple meaning for {normalized_word}.",
        bangla_meaning=clean_text(content.get("bangla_meaning")) or None,
        phonetic=clean_text(content.get("phonetic")) or None,
        synonym=_clean_relation_candidate(content.get("synonym"), normalized_word, allow_phrase=True) or None,
        memory_trick=clean_text(content.get("memory_trick")) or None,
        topic=clean_text(content.get("topic")) or "general",
        sentence=clean_text(content.get("sentence")) or None,
        created_at=date.today(),
    )
    db.session.add(word)
    db.session.commit()
    invalidate_word_list_cache()
    setattr(word, "synonym_hint", _clean_relation_candidate(word.synonym, normalized_word, allow_phrase=True) or _clean_relation_candidate(content.get("synonym"), normalized_word, allow_phrase=True) or None)
    setattr(word, "antonym_hint", _clean_relation_candidate(FALLBACK_RELATIONS.get(normalized_word, {}).get("antonym"), normalized_word, allow_phrase=True) or None)
    setattr(word, "lookup_pending", False)
    return word
