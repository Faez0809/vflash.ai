from collections import defaultdict
from datetime import datetime
import os
import random
import re
import threading
import time

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
from app.services.enrichment_engine import generate_enrichment_payload, validate_enrichment, calculate_quality_score


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
    word = vocabulary.word if vocabulary else (payload.get("word") or "")
    mapped_payload = {
        "definition": payload.get("meaning") or payload.get("definition"),
        "bangla_meaning": payload.get("bangla_meaning"),
        "pronunciation": payload.get("phonetic") or payload.get("pronunciation"),
        "example_sentence": payload.get("sentence") or payload.get("example_sentence"),
        "synonyms": payload.get("synonym") or payload.get("synonyms"),
        "antonyms": payload.get("antonym") or payload.get("antonyms"),
        "part_of_speech": payload.get("part_of_speech"),
    }
    validation_res = validate_enrichment(word, mapped_payload)
    return {
        "valid": validation_res["valid"],
        "errors": validation_res["errors"],
        "definition": mapped_payload["definition"],
        "bangla_meaning": mapped_payload["bangla_meaning"],
        "pronunciation": mapped_payload["pronunciation"],
        "example_sentence": mapped_payload["example_sentence"] if "missing_example_sentence" not in validation_res["errors"] else None,
        "part_of_speech": mapped_payload["part_of_speech"] or None,
        "synonyms": mapped_payload["synonyms"],
        "antonyms": mapped_payload["antonyms"],
    }


def audit_enrichment(vocabulary, enrichment):
    if enrichment is None:
        return {
            "passed": False,
            "score": 0,
            "flags": ["missing_enrichment"],
            "missing_fields": ["definition", "pronunciation", "example_sentence"],
        }

    word = vocabulary.word if vocabulary else (getattr(enrichment, "word", None) or "")
    payload = {
        "definition": enrichment.definition,
        "bangla_meaning": enrichment.bangla_meaning,
        "pronunciation": enrichment.pronunciation,
        "example_sentence": enrichment.example_sentence,
        "synonyms": enrichment.synonyms,
        "antonyms": enrichment.antonyms,
        "part_of_speech": enrichment.part_of_speech,
    }

    validation_res = validate_enrichment(word, payload)
    score = calculate_quality_score(word, payload)

    flags = validation_res["errors"]
    word_validation = normalize_and_validate_word(word, level=vocabulary.level if vocabulary else None, allow_ai=False)
    flags = sorted(list(set(flags + word_validation["flags"])))

    missing_fields = []
    for err in validation_res["errors"]:
        if err.startswith("missing_"):
            field = err.replace("missing_", "")
            if field == "meaning":
                field = "definition"
            elif field == "sentence":
                field = "example_sentence"
            missing_fields.append(field)

    return {
        "passed": validation_res["valid"] and len(word_validation["flags"]) == 0,
        "score": score,
        "flags": flags,
        "missing_fields": sorted(list(set(missing_fields))),
    }


def apply_enrichment_audit(vocabulary, enrichment):
    result = audit_enrichment(vocabulary, enrichment)
    enrichment.enrichment_quality_score = result["score"]
    enrichment.audit_flags = ",".join(result["flags"]) if result["flags"] else None
    enrichment.quality_verified = result["passed"]
    
    # Strictly enforce validation status matching the quality metrics
    if enrichment.corrected_manually:
        enrichment.validation_status = "approved"
    elif result["passed"] and result["score"] >= 80:
        enrichment.validation_status = "approved"
    else:
        enrichment.validation_status = "passed" if result["passed"] else "failed"

    if not enrichment.generation_timestamp:
        enrichment.generation_timestamp = datetime.utcnow()
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
    
    existing = vocabulary.enrichment
    
    # Priority 1 & 2: verified cached or high-score generated enrichments
    if existing is not None:
        if existing.corrected_manually:
            return existing
        
        audit = audit_enrichment(vocabulary, existing)
        if audit["passed"] and audit["score"] >= 80:
            # High-score enrichment; promote to "approved" if it is not already
            if existing.validation_status != "approved" or not existing.quality_verified:
                existing.validation_status = "approved"
                existing.quality_verified = True
                existing.enrichment_quality_score = audit["score"]
                existing.audit_flags = ",".join(audit["flags"]) if audit["flags"] else None
                db.session.commit()
            return existing

    # Priority 3: Live generation fallback (if not allowed or fails, we return current/None)
    if not allow_ai:
        return existing

    from flask import current_app
    try:
        payload = generate_enrichment_payload(vocabulary.word, level=vocabulary.level)
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Groq API generation failed for '{vocabulary.word}': {e}")
        return existing

    validation = validate_enrichment(vocabulary.word, payload)
    score = calculate_quality_score(vocabulary.word, payload)

    if not validation["valid"]:
        # If validation fails: DO NOT cache permanently.
        # Mark vocabulary as needing admin review.
        vocabulary.needs_admin_review = True
        errors_joined = ", ".join(validation["errors"])
        vocabulary.review_reason = f"AI enrichment failed validation: {errors_joined}"
        _flag_vocabulary(
            vocabulary,
            "invalid_english",
            original_word=vocabulary.word,
            notes=f"Rejected enrichment. Validation errors: {errors_joined}"
        )
        db.session.commit()
        return existing

    # If validation passes: save/overwrite cache permanently
    if existing is not None:
        current_score = existing.enrichment_quality_score or 0
        if score > current_score:
            # Overwrite weak cache with superior newly generated one
            existing.definition = payload["definition"]
            existing.bangla_meaning = payload["bangla_meaning"]
            existing.pronunciation = payload["pronunciation"]
            existing.synonyms = payload["synonyms"]
            existing.antonyms = payload["antonyms"]
            existing.example_sentence = payload["example_sentence"]
            existing.part_of_speech = payload["part_of_speech"]
            existing.enrichment_quality_score = score
            existing.last_regenerated_at = datetime.utcnow()
            
            apply_enrichment_audit(vocabulary, existing)
            db.session.commit()
            return existing
        else:
            # Keep existing as it is better or equal
            return existing
    else:
        # Create a new enrichment record
        enrichment = VocabularyEnrichment(
            vocabulary_id=vocabulary.id,
            definition=payload["definition"],
            bangla_meaning=payload["bangla_meaning"],
            pronunciation=payload["pronunciation"],
            synonyms=payload["synonyms"],
            antonyms=payload["antonyms"],
            example_sentence=payload["example_sentence"],
            memory_tip=None,
            part_of_speech=payload["part_of_speech"],
            enrichment_quality_score=score,
            generation_timestamp=datetime.utcnow(),
            generated_by_model=os.environ.get("GROQ_MODEL") or "llama-3.3-70b-versatile",
            corrected_manually=False,
            generated_at=datetime.utcnow(),
            last_regenerated_at=None,
        )
        apply_enrichment_audit(vocabulary, enrichment)
        db.session.add(enrichment)
        db.session.flush()
        vocabulary.enrichment = enrichment
        db.session.commit()
        return enrichment


def regenerate_vocabulary_enrichment(vocabulary, admin_prompt=None):
    if vocabulary.enrichment is not None:
        db.session.delete(vocabulary.enrichment)
        vocabulary.enrichment = None
        db.session.flush()
    enrichment = get_or_create_enrichment(vocabulary, allow_ai=True)
    if enrichment is not None:
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
    try:
        res = generate_enrichment_payload(normalized_word)
        return {
            "word": res["word"],
            "part_of_speech": res["part_of_speech"],
            "meaning": res["definition"],
            "bangla_meaning": res["bangla_meaning"],
            "phonetic": res["pronunciation"],
            "sentence": res["example_sentence"],
            "synonym": res["synonyms"],
            "antonym": res["antonyms"],
            "topic": "general"
        }
    except Exception:
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


def _get_approved_unseen_words(user_id, level, count):
    """Return unseen vocabulary that already have high-quality approved enrichments.
    Used for cache-first flashcard delivery so ready cards appear instantly.
    """
    level = normalize_level(level)
    return (
        VocabularyMaster.query
        .options(selectinload(VocabularyMaster.enrichment))
        .join(VocabularyEnrichment, VocabularyEnrichment.vocabulary_id == VocabularyMaster.id)
        .filter(
            VocabularyMaster.level == level,
            VocabularyMaster.needs_admin_review.is_(False),
            VocabularyEnrichment.validation_status == "approved",
            VocabularyEnrichment.enrichment_quality_score >= HIGH_QUALITY_SCORE,
            ~VocabularyMaster.id.in_(_excluded_generated_or_learned_subquery(user_id)),
        )
        .order_by(
            VocabularyEnrichment.enrichment_quality_score.desc(),
            VocabularyMaster.word.asc(),
        )
        .limit(count)
        .all()
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

def is_session_generation_complete(session):
    """Return True when every session word either has an enrichment or is
    permanently blocked (needs_admin_review). The background worker will have
    already attempted replacements for blocked words.
    """
    for sw in session.session_words:
        vocab = sw.vocabulary
        if vocab is None:
            continue
        # Only block completion if there is no enrichment AND the word is not
        # yet flagged as permanently unresolvable.
        if vocab.enrichment is None and not vocab.needs_admin_review:
            return False
    return True


def get_replacement_vocabulary(user_id, level, order_mode, excluded_ids):
    level = normalize_level(level)
    order_mode = normalize_order_mode(order_mode)
    
    if order_mode in ("review", "mixed_review"):
        # Fetch high-quality review candidate that is not already in this session
        query = (
            UserWordProgress.query.join(VocabularyMaster)
            .filter(
                UserWordProgress.user_id == user_id,
                VocabularyMaster.level == level,
                ~UserWordProgress.vocabulary_id.in_(excluded_ids),
                VocabularyMaster.needs_admin_review == False
            )
        )
        if order_mode == "review":
            query = query.filter(UserWordProgress.is_difficult.is_(True))
            
        review_progress = query.order_by(func.random()).first()
        if review_progress:
            return review_progress.vocabulary

    # Fallback to unseen words
    query = _base_unseen_query(user_id, level)
    if excluded_ids:
        query = query.filter(~VocabularyMaster.id.in_(excluded_ids))
    query = query.filter(VocabularyMaster.needs_admin_review == False)
    candidate = query.order_by(func.random()).first()
    return candidate


def start_background_enrichment(app, session_id):
    def run():
        with app.app_context():
            session = db.session.get(FlashcardSession, session_id)
            if not session:
                return

            total_retries = 0
            max_session_retries = 15
            position = 2

            while position <= session.generated_count:
                try:
                    sw = FlashcardSessionWord.query.filter_by(session_id=session_id, position=position).first()
                    if not sw:
                        break

                    vocab = sw.vocabulary
                    enrichment = get_or_create_enrichment(vocab, allow_ai=True)

                    if enrichment and not vocab.needs_admin_review:
                        position += 1
                    else:
                        # Attempt to replace failed word
                        if total_retries >= max_session_retries:
                            app.logger.warning(f"[EXACT COUNT] Max retries reached for session {session_id}.")
                            position += 1
                            continue

                        excluded_ids = {item.vocabulary_id for item in session.session_words}
                        replacement = get_replacement_vocabulary(session.user_id, session.level, session.order_mode, excluded_ids)
                        if replacement:
                            total_retries += 1
                            app.logger.info(f"[EXACT COUNT] Replacing failed word '{vocab.word}' with '{replacement.word}' at position {position}")
                            
                            sw.vocabulary_id = replacement.id
                            
                            now = datetime.utcnow()
                            progress = UserWordProgress.query.filter_by(
                                user_id=session.user_id,
                                vocabulary_id=replacement.id,
                            ).first()
                            if progress is None:
                                progress = UserWordProgress(user_id=session.user_id, vocabulary_id=replacement.id)
                                db.session.add(progress)
                            progress.is_generated = True
                            progress.times_seen = (progress.times_seen or 0) + 1
                            progress.last_seen_at = now
                            progress.updated_at = now

                            db.session.commit()
                            # Do not increment position, retry this index with replacement word
                        else:
                            app.logger.warning(f"[EXACT COUNT] No replacement available for level {session.level}")
                            position += 1
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"[EXACT COUNT] Exception in background session enrichment: {e}")
                    time.sleep(1.0)
                    position += 1
    threading.Thread(target=run, daemon=True).start()


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
        # CACHE-FIRST: pull words that already have approved enrichments so
        # they are delivered instantly, then fill remaining slots with raw
        # unseen words that will be enriched progressively in the background.
        ready = _get_approved_unseen_words(user_id, level, requested_count)
        if len(ready) >= requested_count:
            vocabularies = ready[:requested_count]
        else:
            ready_ids = {v.id for v in ready}
            remaining_count = requested_count - len(ready)
            # Fetch slightly more than needed to account for id overlap
            raw_candidates = get_unseen_words(
                user_id, level, remaining_count + len(ready_ids), order_mode
            )
            raw = [v for v in raw_candidates if v.id not in ready_ids][:remaining_count]
            # Ready (already-enriched) cards go first so they render instantly
            vocabularies = ready + raw

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
    # Section 4: FIRST CARD EXACT COUNT PRIORITY (Synchronous Retry / Substitution)
    if vocabularies:
        retries = 0
        while retries < 5:
            first_vocab = vocabularies[0]
            enrichment = get_or_create_enrichment(first_vocab, allow_ai=True)
            if enrichment and not first_vocab.needs_admin_review:
                break
            
            # Substitute synchronous first card
            excluded_ids = {v.id for v in vocabularies}
            replacement = get_replacement_vocabulary(user_id, level, order_mode, excluded_ids)
            if not replacement:
                break
            
            vocabularies[0] = replacement
            retries += 1

    for position, vocabulary in enumerate(vocabularies, start=1):
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


class ContinuousEnrichmentWorker:
    _lock = threading.Lock()
    _started = False
    _stop_event = threading.Event()

    @classmethod
    def start(cls, app):
        with cls._lock:
            if cls._started:
                return
            
            # Avoid starting in the Werkzeug reloader master process
            if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
                return
            
            cls._started = True
            cls._stop_event.clear()
            
            raw_app = app._get_current_object() if hasattr(app, "_get_current_object") else app
            
            thread = threading.Thread(
                target=cls._run,
                args=(raw_app,),
                daemon=True,
                name="ContinuousEnrichmentWorker"
            )
            thread.start()
            raw_app.logger.info("[ContinuousEnrichmentWorker] Singleton background worker thread successfully spawned.")

    @classmethod
    def stop(cls):
        with cls._lock:
            cls._stop_event.set()
            cls._started = False

    @classmethod
    def _run(cls, app):
        import time
        from sqlalchemy import or_
        
        levels = ["intermediate", "upper_intermediate", "advanced"]
        level_idx = 0
        
        throttle_interval = float(os.environ.get("CONTINUOUS_WORKER_THROTTLE", "6.0"))
        idle_interval = 45.0
        
        while not cls._stop_event.is_set():
            try:
                with app.app_context():
                    level = levels[level_idx]
                    
                    query = VocabularyMaster.query.outerjoin(VocabularyEnrichment).filter(
                        VocabularyMaster.needs_admin_review == False,
                        VocabularyMaster.level == level
                    ).filter(
                        or_(
                            VocabularyEnrichment.id.is_(None),
                            VocabularyEnrichment.validation_status != "approved",
                            VocabularyEnrichment.enrichment_quality_score < 80
                        )
                    ).order_by(
                        VocabularyMaster.word.asc(),
                        VocabularyMaster.id.asc()
                    )
                    
                    vocab = query.first()
                    
                    if vocab:
                        app.logger.info(f"[ContinuousEnrichmentWorker] Saturation hit: enriching '{vocab.word}' (level: {level})")
                        try:
                            get_or_create_enrichment(vocab, allow_ai=True)
                        except Exception as inner_e:
                            app.logger.error(f"[ContinuousEnrichmentWorker] Error enriching '{vocab.word}': {inner_e}")
                        
                        level_idx = (level_idx + 1) % len(levels)
                        cls._stop_event.wait(throttle_interval)
                    else:
                        has_work = False
                        for other_lvl in levels:
                            other_q = VocabularyMaster.query.outerjoin(VocabularyEnrichment).filter(
                                VocabularyMaster.needs_admin_review == False,
                                VocabularyMaster.level == other_lvl
                            ).filter(
                                or_(
                                    VocabularyEnrichment.id.is_(None),
                                    VocabularyEnrichment.validation_status != "approved",
                                    VocabularyEnrichment.enrichment_quality_score < 80
                                )
                            )
                            if other_q.first():
                                has_work = True
                                break
                        
                        if has_work:
                            level_idx = (level_idx + 1) % len(levels)
                            cls._stop_event.wait(2.0)
                        else:
                            app.logger.info("[ContinuousEnrichmentWorker] All levels fully saturated. Going to idle.")
                            cls._stop_event.wait(idle_interval)
            except Exception as e:
                try:
                    app.logger.error(f"[ContinuousEnrichmentWorker] Exception in loop: {e}")
                except Exception:
                    pass
                time.sleep(10.0)


def start_continuous_enrichment_worker(app):
    ContinuousEnrichmentWorker.start(app)


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
