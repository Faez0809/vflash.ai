import argparse
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import VocabularyMaster, db
from app.services.vocabulary_platform import LEVELS, get_or_create_enrichment, normalize_level


def pregenerate_enrichments(level=None, batch_size=25):
    query = VocabularyMaster.query.filter(~VocabularyMaster.enrichment.has()).order_by(
        VocabularyMaster.level.asc(),
        VocabularyMaster.word.asc(),
    )
    if level:
        query = query.filter(VocabularyMaster.level == normalize_level(level))

    vocabularies = query.limit(max(1, min(int(batch_size), 100))).all()
    generated = 0
    skipped = 0
    for vocabulary in vocabularies:
        if vocabulary.enrichment is not None:
            skipped += 1
            continue
        get_or_create_enrichment(vocabulary, allow_ai=True)
        generated += 1
        if generated % 10 == 0:
            db.session.commit()

    db.session.commit()
    return {"generated": generated, "skipped": skipped}


def parse_args():
    parser = argparse.ArgumentParser(description="Pre-generate cached vocabulary enrichments.")
    parser.add_argument("--level", choices=LEVELS, help="Limit generation to one level.")
    parser.add_argument("--batch-size", type=int, default=25, help="Number of words to enrich in this run.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = create_app()
    with app.app_context():
        result = pregenerate_enrichments(level=args.level, batch_size=args.batch_size)
        print("Enrichment pre-generation summary")
        print(f"Generated: {result['generated']}")
        print(f"Skipped: {result['skipped']}")
