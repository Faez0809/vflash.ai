from collections import Counter
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import VocabularyMaster, db
from app.services.vocabulary_platform import audit_enrichment, normalize_level


def audit_enrichments(level=None, persist=False):
    query = VocabularyMaster.query.order_by(VocabularyMaster.level.asc(), VocabularyMaster.word.asc())
    if level:
        query = query.filter(VocabularyMaster.level == normalize_level(level))

    total_checked = 0
    passed = 0
    flagged = 0
    missing_counter = Counter()
    flag_counter = Counter()

    for vocabulary in query.all():
        total_checked += 1
        result = audit_enrichment(vocabulary, vocabulary.enrichment)
        if result["passed"]:
            passed += 1
        else:
            flagged += 1
        missing_counter.update(result["missing_fields"])
        flag_counter.update(result["flags"])

        if persist and vocabulary.enrichment is not None:
            vocabulary.enrichment.enrichment_quality_score = result["score"]
            vocabulary.enrichment.audit_flags = ",".join(result["flags"]) if result["flags"] else None
            vocabulary.enrichment.quality_verified = result["passed"]

    if persist:
        db.session.commit()

    return {
        "total_checked": total_checked,
        "passed": passed,
        "flagged": flagged,
        "missing_fields": missing_counter,
        "flags": flag_counter,
    }


if __name__ == "__main__":
    level = None
    persist = False
    args = sys.argv[1:]
    if "--persist" in args:
        persist = True
        args.remove("--persist")
    if args:
        level = args[0]

    app = create_app()
    with app.app_context():
        summary = audit_enrichments(level=level, persist=persist)
        print("Enrichment audit summary")
        print(f"Total checked: {summary['total_checked']}")
        print(f"Passed: {summary['passed']}")
        print(f"Flagged: {summary['flagged']}")
        print("Missing fields:")
        for field, count in summary["missing_fields"].most_common():
            print(f"  {field}: {count}")
        print("Flags:")
        for flag, count in summary["flags"].most_common():
            print(f"  {flag}: {count}")
