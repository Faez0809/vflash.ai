from collections import Counter
import csv
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import VocabularyMaster, db
from app.services.vocabulary_platform import normalize_level, normalize_vocab_text, is_phrase


VOCAB_DIR = ROOT_DIR / "VWords"
SOURCE_BOOKS = {
    "intermediate": "intermediate_vocab.csv",
    "upper_intermediate": "upper_intermediate_vocab.csv",
    "advanced": "advanced_vocab.csv",
}


def detect_level(path, row):
    row_level = normalize_level(row.get("level"))
    if row_level:
        return row_level
    filename = path.stem.lower()
    if "upper" in filename:
        return "upper_intermediate"
    if "advanced" in filename:
        return "advanced"
    return "intermediate"


def import_vocabularies():
    imported = 0
    skipped_duplicates = 0
    per_level = Counter()
    seen_in_run = set()

    existing_words = {
        row[0]
        for row in db.session.query(VocabularyMaster.normalized_word).all()
    }

    for path in sorted(VOCAB_DIR.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                word = normalize_vocab_text(row.get("word"))
                if not word:
                    continue
                if word in existing_words or word in seen_in_run:
                    skipped_duplicates += 1
                    continue

                level = detect_level(path, row)
                try:
                    page_no = int(str(row.get("page_no") or "").strip())
                except ValueError:
                    page_no = None

                db.session.add(
                    VocabularyMaster(
                        word=word,
                        normalized_word=word,
                        level=level,
                        page_no=page_no,
                        source_book=SOURCE_BOOKS.get(level, path.name),
                        is_phrase=is_phrase(word),
                    )
                )
                seen_in_run.add(word)
                imported += 1
                per_level[level] += 1

    db.session.commit()
    print("Vocabulary import summary")
    print(f"Imported: {imported}")
    print(f"Skipped duplicates: {skipped_duplicates}")
    for level in ("intermediate", "upper_intermediate", "advanced"):
        print(f"{level}: {per_level[level]}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        import_vocabularies()
