from collections import defaultdict
from datetime import datetime
import os
import random
import re

from sqlalchemy import and_, case, func
from sqlalchemy.orm import selectinload

from app.models import (
    FlashcardSession,
    FlashcardSessionWord,
    SearchVocabulary,
    UserLevelProgress,
    UserWordProgress,
    VocabularyEnrichment,
    VocabularyMaster,
    VocabularyReviewFlag,
    db,
)
from app.services.ai_generator import generate_word_content, suggest_word_corrections
from app.services.stats import clean_text


LEVEL_ALIASES = {
    "beginner": "intermediate",
    "medium": "intermediate",
    "intermediate": "intermediate",
    "upper intermediate": "upper_intermediate",
    "upper_intermediate": "upper_intermediate",
    "upper-intermediate": "upper_intermediate",
    "hard": "advanced",
    "advanced": "advanced",
}
LEVELS = ("intermediate", "upper_intermediate", "advanced")
HIGH_QUALITY_SCORE = 80
BEGINNER_WORDS = {"apple", "book", "cat", "dog", "eat", "food", "good", "happy", "house", "school", "sun", "tree", "water"}
COMMON_CORRECTIONS = {
    "abit": "a bit",
    "alot": "a lot",
    "pineapple pain pol": "pineapple",
}
FLAG_REASONS = {
    "suspicious_ocr": "Possible OCR corruption",
    "too_easy_for_level": "Too basic for advanced level",
    "corrupted_phrase": "Unknown phrase",
    "malformed_word": "Malformed word or phrase",
    "invalid_english": "Invalid English token",
    "duplicate_meaning": "Duplicate semantic entry",
    "low_confidence_correction": "Low AI confidence",
    "repeated_fragments": "Repeated fragments",
    "non_english_token": "Non-English token",
}
PLACEHOLDER_PATTERNS = (
    "a curated vocabulary item",
    "a simple meaning for",
    "definition is being prepared",
    "definition pending review",
    "no bangla translation",
    "no example",
    "no synonym",
    "no antonym",
    "not added yet",
    "n/a",
)


def normalize_vocab_text(value):
    return re.sub(r"\s+", " ", clean_text(value)).strip().lower()


def normalize_level(value):
    normalized = normalize_vocab_text(value).replace("-", "_").replace(" ", "_")
    return LEVEL_ALIASES.get(normalized, normalized if normalized in LEVELS else "intermediate")


def is_phrase(value):
    return len(normalize_vocab_text(value).split()) > 1


def has_display_value(value):
    cleaned = clean_text(value)
    return bool(cleaned) and not any(pattern in cleaned.lower() for pattern in PLACEHOLDER_PATTERNS)


def _flag_vocabulary(vocabulary, flag_type, original_word=None, corrected_word=None, notes=None):
    reason = notes or FLAG_REASONS.get(flag_type, flag_type.replace("_", " "))
    if vocabulary is not None:
        vocabulary.needs_admin_review = True
        vocabulary.review_reason = "; ".join(
            item
            for item in [clean_text(vocabulary.review_reason), clean_text(reason)]
            if item
        )[:1000]
    existing = VocabularyReviewFlag.query.filter_by(
        vocabulary_id=vocabulary.id if vocabulary else None,
        original_word=clean_text(original_word) or (vocabulary.word if vocabulary else ""),
        flag_type=flag_type,
        status="pending",
    ).first()
    if existing is not None:
        return existing
    flag = VocabularyReviewFlag(
        vocabulary_id=vocabulary.id if vocabulary else None,
        original_word=clean_text(original_word) or (vocabulary.word if vocabulary else ""),
        corrected_word=clean_text(corrected_word) or None,
        flag_type=flag_type,
        level=vocabulary.level if vocabulary else None,
        notes=clean_text(reason) or None,
    )
    db.session.add(flag)
    return flag


def _looks_corrupted(value):
    cleaned = clean_text(value)
    compact = re.sub(r"[^A-Za-z]", "", cleaned)
    return (
        not cleaned
        or bool(re.search(r"[^A-Za-z\s'-]", cleaned))
        or len(cleaned.split()) > 5
        or bool(re.search(r"\b[a-z]{1,2}\b\s+\b[a-z]{1,2}\b", cleaned.lower()))
        or (len(compact) >= 8 and not re.search(r"[aeiouy]", compact.lower()))
    )


def _strip_ipa_leftovers(value):
    return re.sub(r"[/\[\]{}()ˈˌËˆËŒ|]", " ", value)


def _has_repeated_fragments(tokens):
    if len(tokens) < 2:
        return False
    return len(set(tokens)) < len(tokens) or any(tokens[index] == tokens[index + 1] for index in range(len(tokens) - 1))


def _known_word_exists(word):
    return bool(word) and VocabularyMaster.query.filter_by(normalized_word=word).first() is not None


def normalize_and_validate_word(raw_word, level=None, allow_ai=True):
    original = clean_text(raw_word)
    cleaned = normalize_vocab_text(_strip_ipa_leftovers(original))
    cleaned = re.sub(r"[^a-z\s'-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '-")
    flags = []
    reasons = []
    corrected = COMMON_CORRECTIONS.get(cleaned, cleaned)
    confidence = 1.0 if corrected != cleaned else 0.8

    if not cleaned:
        flags.append("invalid_english")
    if _looks_corrupted(original):
        flags.append("suspicious_ocr")
    if not re.fullmatch(r"[a-z][a-z\s'-]{1,178}", cleaned or ""):
        flags.append("invalid_english")
    tokens = cleaned.split()
    if corrected != cleaned:
        flags.append("malformed_word")
    if _has_repeated_fragments(tokens):
        flags.append("repeated_fragments")
    if len(tokens) > 1 and any(len(token) <= 2 for token in tokens):
        flags.append("suspicious_ocr")
        flags.append("corrupted_phrase")
    if len(tokens) > 3:
        flags.append("corrupted_phrase")
    if len(tokens) > 1 and len(tokens[0]) >= 4 and re.fullmatch(r"[a-z][a-z'-]*", tokens[0]):
        corrected = tokens[0]
        confidence = max(confidence, 0.9)
        flags.append("malformed_word")
    elif len(tokens) > 1 and cleaned not in COMMON_CORRECTIONS:
        known_token = next((token for token in tokens if len(token) >= 3 and _known_word_exists(token)), None)
        if known_token:
            corrected = known_token
            confidence = max(confidence, 0.85)
            flags.append("malformed_word")

    if flags and corrected == cleaned and allow_ai:
        suggestions = suggest_word_corrections(cleaned, max_suggestions=1)
        if suggestions:
            corrected = normalize_vocab_text(suggestions[0])
            confidence = 0.72
            flags.append("low_confidence_correction")

    if level == "advanced" and corrected in BEGINNER_WORDS:
        flags.append("too_easy_for_level")

    flags = sorted(set(flags))
    reasons = [FLAG_REASONS.get(flag, flag.replace("_", " ")) for flag in flags]
    return {
        "original_word": original,
        "normalized_word": cleaned,
        "corrected_word": corrected,
        "is_valid": bool(corrected) and not any(flag in flags for flag in {"invalid_english", "corrupted_phrase", "repeated_fragments"}),
        "confidence": confidence,
        "flags": flags,
        "reasons": reasons,
        "needs_review": bool(flags) and confidence < 0.95,
    }


def apply_vocabulary_correction(vocabulary, corrected_word, original_word=None, corrected_by_admin=False):
    corrected = normalize_vocab_text(corrected_word)
    if not corrected or corrected == vocabulary.normalized_word:
        return vocabulary
    duplicate = VocabularyMaster.query.filter(
        VocabularyMaster.normalized_word == corrected,
        VocabularyMaster.id != vocabulary.id,
    ).first()
    if duplicate is not None:
        _flag_vocabulary(
            vocabulary,
            "duplicate_meaning",
            original_word=original_word or vocabulary.word,
            corrected_word=corrected,
            notes="Correction matches an existing vocabulary entry.",
        )
        return vocabulary

    vocabulary.original_word = vocabulary.original_word or clean_text(original_word) or vocabulary.word
    vocabulary.word = corrected
    vocabulary.normalized_word = corrected
    vocabulary.is_phrase = is_phrase(corrected)
    vocabulary.corrected_at = datetime.utcnow()
    vocabulary.corrected_by_admin = bool(corrected_by_admin)
    return vocabulary


def preprocess_vocabulary_entry(vocabulary):
    result = normalize_and_validate_word(vocabulary.word, level=vocabulary.level, allow_ai=True)
    corrected = result["corrected_word"]
    for flag in result["flags"]:
        _flag_vocabulary(
            vocabulary,
            flag,
            original_word=result["original_word"],
            corrected_word=corrected if corrected != result["normalized_word"] else None,
            notes=FLAG_REASONS.get(flag),
        )
    if corrected and corrected != vocabulary.normalized_word and result["confidence"] >= 0.85:
        apply_vocabulary_correction(vocabulary, corrected, original_word=result["original_word"])
    vocabulary.last_audited_at = datetime.utcnow()
    return {"original_word": result["original_word"], "corrected_word": vocabulary.word, "flags": result["flags"]}


def normalize_order_mode(value):
    value = normalize_vocab_text(value)
    return value if value in {"alphabetical", "mixed", "regenerate", "review", "mixed_review"} else "alphabetical"


def _is_placeholder(value):
    cleaned = clean_text(value).lower()
    return not cleaned or any(pattern in cleaned for pattern in PLACEHOLDER_PATTERNS)


def _clean_relation(value, normalized_word):
    cleaned = clean_text(value)
    if _is_placeholder(cleaned) or cleaned.lower() == normalized_word:
        return None
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;")
    if not re.fullmatch(r"[A-Za-z][A-Za-z\s,'-]{1,120}", cleaned):
        return None
    return cleaned


def _clean_bangla(value):
    cleaned = clean_text(value)
    if _is_placeholder(cleaned):
        return None
    if not re.search(r"[\u0980-\u09FF]", cleaned):
        return None
    return cleaned[:140].strip()


def _fallback_pronunciation(word):
    cleaned = re.sub(r"[^a-z]", "", normalize_vocab_text(word))
    if not cleaned:
        return None
    vowels = "aeiouy"
    chunks = []
    current = ""
    for index, char in enumerate(cleaned):
        current += char
        has_more_vowels = any(letter in vowels for letter in cleaned[index + 1 :])
        if char in vowels and has_more_vowels and len(current) >= 2:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return "-".join(chunks).capitalize()


def _sentence_mentions_word(sentence, word):
    sentence = clean_text(sentence).lower()
    word = normalize_vocab_text(word)
    if not sentence or not word:
        return False
    if " " in word:
        return word in sentence
    return re.search(rf"\b{re.escape(word)}\b", sentence) is not None


def _valid_pronunciation(value):
    value = clean_text(value)
    if _is_placeholder(value) or len(value) < 3 or len(value) > 80:
        return False
    if re.search(r"[{}<>\\|/\[\]ˈˌ]", value):
        return False
    letters = re.sub(r"[^A-Za-z]", "", value)
    return len(letters) >= 3 and bool(re.search(r"[A-Za-z]-[A-Za-z]", value))


def validate_enrichment_payload(vocabulary, payload):
    normalized_word = vocabulary.normalized_word
    definition = clean_text(payload.get("meaning") or payload.get("definition"))
    pronunciation = clean_text(payload.get("phonetic") or payload.get("pronunciation")) or _fallback_pronunciation(vocabulary.word)
    example_sentence = clean_text(payload.get("sentence") or payload.get("example_sentence"))
    part_of_speech = clean_text(payload.get("part_of_speech"))
    synonyms = _clean_relation(payload.get("synonym") or payload.get("synonyms"), normalized_word)
    antonyms = _clean_relation(payload.get("antonym") or payload.get("antonyms"), normalized_word)
    bangla_meaning = _clean_bangla(payload.get("bangla_meaning"))

    errors = []
    definition_lower = definition.lower()
    if (
        len(definition) < 8
        or len(definition) > 180
        or definition_lower in {normalized_word, vocabulary.word.lower()}
        or _is_placeholder(definition)
        or re.search(r"\b(as an ai|lorem ipsum|undefined|null|cannot provide|i'm sorry)\b", definition_lower)
    ):
        errors.append("definition")
    if not bangla_meaning:
        errors.append("bangla_meaning")
    if not _valid_pronunciation(pronunciation):
        errors.append("pronunciation")
    if (
        not example_sentence
        or len(example_sentence) < 20
        or _is_placeholder(example_sentence)
        or not _sentence_mentions_word(example_sentence, normalized_word)
    ):
        errors.append("example_sentence")
    if synonyms and normalized_word in {normalize_vocab_text(part) for part in re.split(r"[,;]", synonyms)}:
        errors.append("synonyms")
    if antonyms and normalized_word in {normalize_vocab_text(part) for part in re.split(r"[,;]", antonyms)}:
        errors.append("antonyms")

    valid = not errors
    return {
        "valid": valid,
        "errors": errors,
        "definition": definition,
        "bangla_meaning": bangla_meaning,
        "pronunciation": pronunciation,
        "example_sentence": example_sentence if "example_sentence" not in errors else None,
        "part_of_speech": part_of_speech or None,
        "synonyms": synonyms,
        "antonyms": antonyms,
    }


def audit_enrichment(vocabulary, enrichment):
    flags = []
    missing_fields = []
    word_validation = normalize_and_validate_word(vocabulary.word if vocabulary else "", level=vocabulary.level if vocabulary else None, allow_ai=False)
    flags.extend(word_validation["flags"])
    if enrichment is None:
        return {
            "passed": False,
            "score": 0,
            "flags": ["missing_enrichment"],
            "missing_fields": ["definition", "pronunciation", "example_sentence"],
        }

    definition = clean_text(enrichment.definition)
    bangla_meaning = clean_text(enrichment.bangla_meaning)
    pronunciation = clean_text(enrichment.pronunciation)
    example_sentence = clean_text(enrichment.example_sentence)
    synonyms = clean_text(enrichment.synonyms)
    antonyms = clean_text(enrichment.antonyms)
    memory_tip = clean_text(enrichment.memory_tip)
    normalized_word = vocabulary.normalized_word if vocabulary else normalize_vocab_text(getattr(enrichment, "word", ""))

    if not definition:
        flags.append("empty_definition")
        missing_fields.append("definition")
    elif len(definition) < 20:
        flags.append("weak_definition")
    if definition.lower() in {normalized_word, f"a curated vocabulary item: {normalized_word}."} or _is_placeholder(definition):
        flags.append("duplicate_or_placeholder_meaning")
    if re.search(r"\b(as an ai|lorem ipsum|undefined|null|cannot provide|i'm sorry)\b", definition.lower()):
        flags.append("hallucinated_output")
    if not _clean_bangla(bangla_meaning):
        flags.append("weak_bangla_meaning")
        missing_fields.append("bangla_meaning")

    if not pronunciation:
        flags.append("missing_pronunciation")
        missing_fields.append("pronunciation")
    elif not _valid_pronunciation(pronunciation):
        flags.append("malformed_pronunciation")

    if synonyms and not _clean_relation(synonyms, normalized_word):
        flags.append("invalid_synonym")

    if antonyms and not _clean_relation(antonyms, normalized_word):
        flags.append("invalid_antonym")

    if not example_sentence:
        flags.append("missing_example")
        missing_fields.append("example_sentence")
    elif len(example_sentence) < 24:
        flags.append("extremely_short_example")
    elif vocabulary is not None and not _sentence_mentions_word(example_sentence, vocabulary.normalized_word):
        flags.append("irrelevant_example")

    score = 100
    penalties = {
        "empty_definition": 45,
        "weak_definition": 25,
        "duplicate_or_placeholder_meaning": 30,
        "hallucinated_output": 60,
        "missing_pronunciation": 20,
        "malformed_pronunciation": 25,
        "invalid_synonym": 12,
        "invalid_antonym": 10,
        "missing_example": 18,
        "extremely_short_example": 12,
        "irrelevant_example": 20,
        "weak_bangla_meaning": 20,
        "suspicious_ocr": 60,
        "malformed_word": 50,
        "corrupted_phrase": 70,
        "invalid_english": 80,
        "repeated_fragments": 65,
        "non_english_token": 70,
        "too_easy_for_level": 25,
        "low_confidence_correction": 25,
    }
    for flag in flags:
        score -= penalties.get(flag, 5)
    score = max(0, min(100, score))
    return {
        "passed": score >= HIGH_QUALITY_SCORE and not flags,
        "score": score,
        "flags": flags,
        "missing_fields": sorted(set(missing_fields)),
    }


def apply_enrichment_audit(vocabulary, enrichment):
    result = audit_enrichment(vocabulary, enrichment)
    enrichment.enrichment_quality_score = result["score"]
    enrichment.audit_flags = ",".join(result["flags"]) if result["flags"] else None
    enrichment.quality_verified = result["passed"]
    enrichment.last_audited_at = datetime.utcnow()
    if vocabulary is not None:
        vocabulary.last_audited_at = enrichment.last_audited_at
        bad_word_flags = {
            "suspicious_ocr",
            "malformed_word",
            "corrupted_phrase",
            "invalid_english",
            "repeated_fragments",
            "too_easy_for_level",
            "low_confidence_correction",
        }
        flagged = bad_word_flags.intersection(result["flags"])
        if flagged:
            vocabulary.needs_admin_review = True
            vocabulary.review_reason = "; ".join(FLAG_REASONS.get(flag, flag) for flag in sorted(flagged))
    return result


def get_or_create_enrichment(vocabulary, allow_ai=True):
    preprocessing = preprocess_vocabulary_entry(vocabulary)
    if vocabulary.enrichment is not None:
        if (
            preprocessing["original_word"]
            and normalize_vocab_text(preprocessing["original_word"]) != vocabulary.normalized_word
            and not vocabulary.enrichment.corrected_manually
        ):
            db.session.delete(vocabulary.enrichment)
            vocabulary.enrichment = None
            db.session.flush()
        else:
            apply_enrichment_audit(vocabulary, vocabulary.enrichment)
            vocabulary.enrichment.memory_tip = None
            db.session.flush()
            return vocabulary.enrichment

    payload = build_shared_enrichment_payload(vocabulary.normalized_word, allow_ai=allow_ai)

    validation = validate_enrichment_payload(vocabulary, payload)
    definition = validation["definition"] or "Definition pending review."
    if not validation["valid"]:
        for error in validation["errors"]:
            _flag_vocabulary(vocabulary, "invalid_english", original_word=vocabulary.word, notes=f"Rejected enrichment field: {error}")
        if not _valid_pronunciation(validation["pronunciation"]):
            validation["pronunciation"] = None
        if "definition" in validation["errors"]:
            definition = "Definition pending review."

    enrichment = VocabularyEnrichment(
        vocabulary_id=vocabulary.id,
        definition=definition,
        bangla_meaning=validation["bangla_meaning"],
        pronunciation=validation["pronunciation"],
        synonyms=validation["synonyms"],
        antonyms=validation["antonyms"],
        example_sentence=validation["example_sentence"],
        memory_tip=None,
        part_of_speech=validation["part_of_speech"],
        quality_verified=validation["valid"],
        enrichment_quality_score=0,
        generated_by_model=os.environ.get("GROQ_MODEL") or None,
        corrected_manually=False,
        generated_at=datetime.utcnow(),
        last_regenerated_at=None,
    )
    apply_enrichment_audit(vocabulary, enrichment)
    db.session.add(enrichment)
    db.session.flush()
    vocabulary.enrichment = enrichment
    return enrichment


def regenerate_vocabulary_enrichment(vocabulary, admin_prompt=None):
    if vocabulary.enrichment is not None:
        db.session.delete(vocabulary.enrichment)
        vocabulary.enrichment = None
        db.session.flush()
    enrichment = get_or_create_enrichment(vocabulary, allow_ai=True)
    if admin_prompt:
        enrichment.audit_flags = ",".join(filter(None, [enrichment.audit_flags, "admin_prompt_override"]))
    enrichment.last_regenerated_at = datetime.utcnow()
    enrichment.corrected_manually = False
    apply_enrichment_audit(vocabulary, enrichment)
    return enrichment


def build_shared_enrichment_payload(word, allow_ai=True):
    normalized_word = normalize_vocab_text(word)
    if not normalized_word or not allow_ai:
        return {}
    return generate_word_content(normalized_word) or {}


def create_search_vocabulary_from_payload(user_id, normalized_word, payload):
    temp_vocabulary = VocabularyMaster(
        word=clean_text(payload.get("word")) or normalized_word,
        normalized_word=normalized_word,
        level=normalize_level(payload.get("difficulty") or "intermediate"),
        is_phrase=is_phrase(normalized_word),
    )
    validation = validate_enrichment_payload(temp_vocabulary, payload)
    return SearchVocabulary(
        word=clean_text(payload.get("word")) or normalized_word,
        normalized_word=normalized_word,
        searched_by_user_id=user_id,
        definition=validation["definition"] if validation["valid"] else None,
        bangla_meaning=validation["bangla_meaning"],
        pronunciation=validation["pronunciation"] if _valid_pronunciation(validation["pronunciation"]) else None,
        synonyms=validation["synonyms"],
        antonyms=validation["antonyms"],
        example_sentence=validation["example_sentence"],
        part_of_speech=validation["part_of_speech"],
        difficulty_estimate=clean_text(payload.get("difficulty")) or None,
        source_type="search",
        ai_generated=bool(payload),
    )


def _bounded_count(count):
    return 10 if int(count or 0) == 10 else 5


def get_or_create_level_progress(user_id, level):
    level = normalize_level(level)
    progress = UserLevelProgress.query.filter_by(user_id=user_id, level=level).first()
    if progress is None:
        progress = UserLevelProgress(user_id=user_id, level=level)
        db.session.add(progress)
        db.session.flush()
    return progress


def _excluded_generated_or_learned_subquery(user_id):
    return (
        db.session.query(UserWordProgress.vocabulary_id)
        .filter(
            UserWordProgress.user_id == user_id,
            (UserWordProgress.is_generated.is_(True)) | (UserWordProgress.is_learned.is_(True)),
        )
        .subquery()
    )


def _base_unseen_query(user_id, level):
    return (
        VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment))
        .filter(VocabularyMaster.level == normalize_level(level))
        .filter(~VocabularyMaster.id.in_(_excluded_generated_or_learned_subquery(user_id)))
    )


def _update_level_completion(user_id, level, last_word_id=None):
    level = normalize_level(level)
    state = get_or_create_level_progress(user_id, level)
    total = VocabularyMaster.query.filter_by(level=level).count()
    learned = (
        UserWordProgress.query.join(VocabularyMaster)
        .filter(
            UserWordProgress.user_id == user_id,
            UserWordProgress.is_learned.is_(True),
            VocabularyMaster.level == level,
        )
        .count()
    )
    state.completed_percentage = round((learned / total) * 100, 2) if total else 0
    if last_word_id is not None:
        state.last_alphabetical_word_id = last_word_id
    state.updated_at = datetime.utcnow()
    return state


def get_unseen_words(user_id, level, count=5, order_mode="alphabetical"):
    level = normalize_level(level)
    order_mode = normalize_order_mode(order_mode)
    count = _bounded_count(count)

    query = _base_unseen_query(user_id, level)
    if order_mode == "alphabetical":
        level_state = get_or_create_level_progress(user_id, level)
        if level_state.last_alphabetical_word_id:
            last_word = db.session.get(VocabularyMaster, level_state.last_alphabetical_word_id)
            if last_word is not None:
                query = query.filter(VocabularyMaster.word > last_word.word)
        candidates = query.order_by(VocabularyMaster.word.asc(), VocabularyMaster.id.asc()).limit(count).all()
        if len(candidates) < count:
            selected_ids = {item.id for item in candidates}
            fallback_query = _base_unseen_query(user_id, level)
            if selected_ids:
                fallback_query = fallback_query.filter(~VocabularyMaster.id.in_(selected_ids))
            candidates += fallback_query.order_by(VocabularyMaster.word.asc(), VocabularyMaster.id.asc()).limit(count - len(candidates)).all()
        return candidates[:count]

    recent_seen = (
        db.session.query(UserWordProgress.vocabulary_id)
        .filter(UserWordProgress.user_id == user_id, UserWordProgress.last_seen_at.isnot(None))
        .order_by(UserWordProgress.last_seen_at.desc())
        .limit(40)
        .subquery()
    )
    candidates = query.filter(~VocabularyMaster.id.in_(recent_seen)).order_by(func.random()).limit(max(count * 3, 18)).all()
    if len(candidates) < count:
        candidates += query.order_by(func.random()).limit(count - len(candidates)).all()
    if order_mode == "mixed":
        random.shuffle(candidates)
    return candidates[:count]


def get_review_words(user_id, level=None, count=5):
    count = _bounded_count(count)
    query = (
        UserWordProgress.query.options(
            selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
        )
        .join(VocabularyMaster)
        .filter(UserWordProgress.user_id == user_id)
        .filter(UserWordProgress.is_difficult.is_(True))
    )
    if level:
        query = query.filter(VocabularyMaster.level == normalize_level(level))
    return (
        query.order_by(
            UserWordProgress.is_difficult.desc(),
            UserWordProgress.times_reviewed.asc(),
            UserWordProgress.last_reviewed_at.asc().nullsfirst(),
            UserWordProgress.updated_at.asc(),
        )
        .limit(count)
        .all()
    )


def get_mixed_words(user_id, level, count=5):
    count = _bounded_count(count)
    review_count = max(1, count // 2)
    review_items = get_review_words(user_id, level=level, count=review_count)
    review_vocab_ids = {item.vocabulary_id for item in review_items}
    unseen_vocabularies = [
        item
        for item in get_unseen_words(user_id, level, count=count, order_mode="mixed")
        if item.id not in review_vocab_ids
    ]
    return review_items, unseen_vocabularies[: max(0, count - len(review_items))]


def select_unseen_vocabularies(user_id, level, count, order_mode):
    return get_unseen_words(user_id, level, count=count, order_mode=order_mode)


def create_flashcard_session(user_id, level, requested_count, order_mode, include_generated=False):
    requested_count = _bounded_count(requested_count)
    level = normalize_level(level)
    order_mode = normalize_order_mode(order_mode)
    review_progress_items = []

    if order_mode == "review":
        review_progress_items = get_review_words(user_id, level=level, count=requested_count)
        vocabularies = [item.vocabulary for item in review_progress_items]
    elif order_mode == "mixed_review":
        review_progress_items, vocabularies = get_mixed_words(user_id, level, count=requested_count)
        vocabularies = [item.vocabulary for item in review_progress_items] + vocabularies
    elif order_mode == "regenerate" or include_generated:
        vocabularies = (
            VocabularyMaster.query.options(selectinload(VocabularyMaster.enrichment))
            .join(UserWordProgress, UserWordProgress.vocabulary_id == VocabularyMaster.id)
            .filter(
                UserWordProgress.user_id == user_id,
                VocabularyMaster.level == level,
                UserWordProgress.is_learned.is_(False),
            )
            .order_by(UserWordProgress.last_seen_at.asc().nullsfirst(), VocabularyMaster.id.asc())
            .limit(requested_count)
            .all()
        )
        if len(vocabularies) < requested_count:
            seen_ids = {item.id for item in vocabularies}
            vocabularies += [
                item
                for item in get_unseen_words(user_id, level, requested_count - len(vocabularies), "mixed")
                if item.id not in seen_ids
            ]
    else:
        vocabularies = get_unseen_words(user_id, level, requested_count, order_mode)

    session = FlashcardSession(
        user_id=user_id,
        level=level,
        requested_count=requested_count,
        generated_count=len(vocabularies),
        order_mode=order_mode,
    )
    db.session.add(session)
    db.session.flush()

    now = datetime.utcnow()
    for position, vocabulary in enumerate(vocabularies, start=1):
        get_or_create_enrichment(vocabulary, allow_ai=True)
        progress = UserWordProgress.query.filter_by(
            user_id=user_id,
            vocabulary_id=vocabulary.id,
        ).first()
        if progress is None:
            progress = UserWordProgress(user_id=user_id, vocabulary_id=vocabulary.id)
            db.session.add(progress)
        progress.is_generated = True
        progress.times_seen = (progress.times_seen or 0) + 1
        progress.last_seen_at = now
        progress.updated_at = now
        db.session.add(
            FlashcardSessionWord(
                session_id=session.id,
                vocabulary_id=vocabulary.id,
                position=position,
            )
        )

    if vocabularies and order_mode == "alphabetical":
        _update_level_completion(user_id, level, last_word_id=vocabularies[-1].id)
    else:
        _update_level_completion(user_id, level)

    return session


def get_session_progress_words(user_id, session_id, include_learned=False):
    rows = (
        UserWordProgress.query.options(
            selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
        )
        .join(FlashcardSessionWord, FlashcardSessionWord.vocabulary_id == UserWordProgress.vocabulary_id)
        .filter(UserWordProgress.user_id == user_id, FlashcardSessionWord.session_id == session_id)
        .order_by(FlashcardSessionWord.position.asc())
    )
    if not include_learned:
        rows = rows.filter(UserWordProgress.is_learned.is_(False))
    return rows.all()


def get_all_generated_progress_words(user_id):
    return (
        UserWordProgress.query.options(
            selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
        )
        .filter(UserWordProgress.user_id == user_id, UserWordProgress.is_generated.is_(True))
        .order_by(UserWordProgress.last_seen_at.desc().nullslast(), UserWordProgress.created_at.desc())
        .all()
    )


def get_difficult_progress_words(user_id):
    return (
        UserWordProgress.query.options(
            selectinload(UserWordProgress.vocabulary).selectinload(VocabularyMaster.enrichment)
        )
        .filter(UserWordProgress.user_id == user_id, UserWordProgress.is_difficult.is_(True))
        .order_by(UserWordProgress.last_reviewed_at.asc().nullsfirst(), UserWordProgress.updated_at.desc())
        .all()
    )


def mark_progress_learned(progress):
    now = datetime.utcnow()
    progress.is_learned = True
    progress.is_reviewed = True
    progress.last_reviewed_at = now
    progress.updated_at = now
    progress.times_reviewed = (progress.times_reviewed or 0) + 1


def mark_progress_reviewed(progress):
    now = datetime.utcnow()
    progress.is_reviewed = True
    progress.last_reviewed_at = now
    progress.updated_at = now
    progress.times_reviewed = (progress.times_reviewed or 0) + 1


def cache_search_vocabulary(user_id, word, payload=None):
    normalized_word = normalize_vocab_text(word)
    if not normalized_word:
        return None
    tokens = normalized_word.split()
    if len(tokens) > 1 and len(tokens[0]) >= 4 and re.fullmatch(r"[a-z][a-z'-]*", tokens[0]):
        normalized_word = tokens[0]
    elif _looks_corrupted(normalized_word):
        suggestions = suggest_word_corrections(normalized_word, max_suggestions=1)
        if suggestions:
            normalized_word = normalize_vocab_text(suggestions[0])

    existing = SearchVocabulary.query.filter_by(normalized_word=normalized_word).first()
    if existing is not None:
        return existing

    payload = payload or build_shared_enrichment_payload(normalized_word, allow_ai=True)
    search_word = create_search_vocabulary_from_payload(user_id, normalized_word, payload)
    db.session.add(search_word)
    db.session.flush()
    return search_word


def calculate_level_progress(user_id):
    totals = dict(
        db.session.query(VocabularyMaster.level, func.count(VocabularyMaster.id))
        .group_by(VocabularyMaster.level)
        .all()
    )
    progress_rows = (
        db.session.query(
            VocabularyMaster.level,
            func.coalesce(func.sum(case((UserWordProgress.is_generated.is_(True), 1), else_=0)), 0),
            func.coalesce(func.sum(case((UserWordProgress.is_learned.is_(True), 1), else_=0)), 0),
        )
        .outerjoin(
            UserWordProgress,
            and_(
                UserWordProgress.vocabulary_id == VocabularyMaster.id,
                UserWordProgress.user_id == user_id,
            ),
        )
        .group_by(VocabularyMaster.level)
        .all()
    )
    by_level = defaultdict(
        lambda: {
            "total_words": 0,
            "generated": 0,
            "learned": 0,
            "unseen_remaining": 0,
            "difficult": 0,
            "review_queue": 0,
            "completion": 0,
        }
    )
    for level in LEVELS:
        by_level[level]["total_words"] = int(totals.get(level, 0) or 0)
        by_level[level]["unseen_remaining"] = int(totals.get(level, 0) or 0)
    for level, generated, learned in progress_rows:
        total = int(totals.get(level, 0) or 0)
        learned = int(learned or 0)
        by_level[level] = {
            "total_words": total,
            "generated": int(generated or 0),
            "learned": learned,
            "unseen_remaining": max(0, total - int(generated or 0)),
            "difficult": 0,
            "review_queue": 0,
            "completion": round((learned / total) * 100, 1) if total else 0,
        }
    review_rows = (
        db.session.query(
            VocabularyMaster.level,
            func.coalesce(func.sum(case((UserWordProgress.is_difficult.is_(True), 1), else_=0)), 0),
        )
        .join(UserWordProgress, UserWordProgress.vocabulary_id == VocabularyMaster.id)
        .filter(UserWordProgress.user_id == user_id)
        .group_by(VocabularyMaster.level)
        .all()
    )
    for level, difficult in review_rows:
        by_level[level]["difficult"] = int(difficult or 0)
        by_level[level]["review_queue"] = int(difficult or 0)
    return dict(by_level)
