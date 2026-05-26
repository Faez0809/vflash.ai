import argparse
from datetime import datetime
import os
from pathlib import Path
import sys

from sqlalchemy import or_


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import VocabularyEnrichment, VocabularyMaster, db
from app.services.ai_generator import generate_word_content
from app.services.vocabulary_platform import (
    HIGH_QUALITY_SCORE,
    LEVELS,
    apply_enrichment_audit,
    get_or_create_enrichment,
    normalize_level,
    validate_enrichment_payload,
)


def _is_flagged(enrichment):
    if enrichment is None:
        return True
    return (
        not enrichment.quality_verified
        or (enrichment.enrichment_quality_score or 0) < HIGH_QUALITY_SCORE
        or bool(enrichment.audit_flags)
    )


def regenerate_enrichments(level=None, word=None, batch_size=25):
    query = (
        VocabularyMaster.query.outerjoin(VocabularyEnrichment)
        .filter(
            or_(
                VocabularyEnrichment.id.is_(None),
                VocabularyEnrichment.quality_verified.is_(False),
                VocabularyEnrichment.enrichment_quality_score < HIGH_QUALITY_SCORE,
                VocabularyEnrichment.audit_flags.isnot(None),
            )
        )
        .order_by(VocabularyMaster.level.asc(), VocabularyMaster.word.asc())
    )
    if level:
        query = query.filter(VocabularyMaster.level == normalize_level(level))
    if word:
        query = query.filter(VocabularyMaster.normalized_word == word.strip().lower())

    regenerated = 0
    skipped_valid = 0
    skipped_manual = 0
    failed = 0
    for vocabulary in query.limit(max(1, min(int(batch_size), 100))).all():
        enrichment = vocabulary.enrichment
        if enrichment is not None and enrichment.corrected_manually:
            skipped_manual += 1
            continue
        if enrichment is not None and not _is_flagged(enrichment):
            skipped_valid += 1
            continue
        if enrichment is not None and (enrichment.enrichment_quality_score or 0) >= HIGH_QUALITY_SCORE:
            skipped_valid += 1
            continue

        payload = generate_word_content(vocabulary.normalized_word) or {}
        validation = validate_enrichment_payload(vocabulary, payload)
        if not validation["valid"]:
            failed += 1
            if enrichment is None:
                get_or_create_enrichment(vocabulary, allow_ai=False)
            else:
                apply_enrichment_audit(vocabulary, enrichment)
            continue

        enrichment = enrichment or get_or_create_enrichment(vocabulary, allow_ai=False)
        enrichment.definition = validation["definition"]
        enrichment.bangla_meaning = str(payload.get("bangla_meaning") or "").strip() or None
        enrichment.pronunciation = validation["pronunciation"]
        enrichment.synonyms = validation["synonyms"]
        enrichment.antonyms = validation["antonyms"]
        enrichment.example_sentence = validation["example_sentence"]
        enrichment.memory_tip = str(payload.get("memory_trick") or payload.get("memory_tip") or "").strip() or None
        enrichment.part_of_speech = validation["part_of_speech"]
        enrichment.generated_by_model = os.environ.get("GROQ_MODEL") or enrichment.generated_by_model
        enrichment.generated_at = datetime.utcnow()
        enrichment.corrected_manually = False
        apply_enrichment_audit(vocabulary, enrichment)
        regenerated += 1

        if regenerated % 10 == 0:
            db.session.commit()

    db.session.commit()
    return {
        "regenerated": regenerated,
        "skipped_valid": skipped_valid,
        "skipped_manual": skipped_manual,
        "failed": failed,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Regenerate only flagged vocabulary enrichments.")
    parser.add_argument("--level", choices=LEVELS, help="Limit to one level.")
    parser.add_argument("--word", help="Regenerate one normalized word.")
    parser.add_argument("--batch-size", type=int, default=25, help="Maximum rows to inspect.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = create_app()
    with app.app_context():
        result = regenerate_enrichments(level=args.level, word=args.word, batch_size=args.batch_size)
        print("Enrichment regeneration summary")
        print(f"Regenerated: {result['regenerated']}")
        print(f"Skipped valid: {result['skipped_valid']}")
        print(f"Skipped manual: {result['skipped_manual']}")
        print(f"Failed validation: {result['failed']}")
