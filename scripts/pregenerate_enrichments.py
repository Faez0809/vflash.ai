import argparse
from pathlib import Path
import sys
import time
from sqlalchemy import or_

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import VocabularyMaster, VocabularyEnrichment, db
from app.services.vocabulary_platform import LEVELS, get_or_create_enrichment, normalize_level


def pregenerate_enrichments(level=None, batch_size=25, throttle=1.0):
    query = VocabularyMaster.query.outerjoin(VocabularyEnrichment).filter(
        VocabularyMaster.needs_admin_review == False
    )
    if level:
        query = query.filter(VocabularyMaster.level == normalize_level(level))

    # Query for vocabulary words missing verified cached enrichments:
    # 1. Enrichment is missing completely
    # 2. Or is not yet "approved"
    # 3. Or has a quality score under 80
    query = query.filter(
        or_(
            VocabularyEnrichment.id.is_(None),
            VocabularyEnrichment.validation_status != "approved",
            VocabularyEnrichment.enrichment_quality_score < 80
        )
    ).order_by(
        VocabularyMaster.level.asc(),
        VocabularyMaster.word.asc(),
    )

    vocabularies = query.limit(max(1, min(int(batch_size), 500))).all()
    generated = 0
    skipped = 0
    failed = 0

    print(f"Found {len(vocabularies)} words to process.")

    for index, vocabulary in enumerate(vocabularies, start=1):
        try:
            print(f"[{index}/{len(vocabularies)}] Processing '{vocabulary.word}' (level: {vocabulary.level})...")
            enrichment = get_or_create_enrichment(vocabulary, allow_ai=True)
            
            if enrichment and enrichment.validation_status == "approved":
                generated += 1
                print(f"  -> SUCCESS: Cache verified (score: {enrichment.enrichment_quality_score})")
            else:
                if vocabulary.needs_admin_review:
                    failed += 1
                    print(f"  -> WARNING: Failed validation. Marked for admin review. Reason: {vocabulary.review_reason}")
                else:
                    skipped += 1
                    print(f"  -> INFO: Processed but not approved.")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            failed += 1
            print(f"  -> ERROR: Exception while processing '{vocabulary.word}': {e}", file=sys.stderr)

        if index < len(vocabularies) and throttle > 0:
            time.sleep(throttle)

    return {"generated": generated, "skipped": skipped, "failed": failed}


def parse_args():
    parser = argparse.ArgumentParser(description="Pre-generate cached vocabulary enrichments.")
    parser.add_argument("--level", choices=LEVELS, help="Limit generation to one level.")
    parser.add_argument("--batch-size", type=int, default=25, help="Number of words to enrich in this run.")
    parser.add_argument("--throttle", type=float, default=1.0, help="Throttle delay (in seconds) between requests.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = create_app()
    with app.app_context():
        result = pregenerate_enrichments(
            level=args.level, 
            batch_size=args.batch_size,
            throttle=args.throttle
        )
        print("\n=== Enrichment Pregeneration Worker Summary ===")
        print(f"Newly Generated & Approved: {result['generated']}")
        print(f"Skipped / Unchanged: {result['skipped']}")
        print(f"Failed / Flagged for Admin: {result['failed']}")
        print("================================================\n")
