import argparse

from app import create_app
from app.models import Word, db
from app.services.learning_content import invalidate_word_list_cache
from app.services.word_validation import mark_word_invalid, validate_word_model


def clean_invalid_words(delete_invalid=False, limit=None):
    query = Word.query.order_by(Word.id.asc())
    if limit:
        query = query.limit(limit)

    scanned = 0
    invalid_count = 0
    deleted_count = 0
    marked_count = 0
    invalid_examples = []

    for word in query.all():
        scanned += 1
        validation = validate_word_model(word, topic_hint="")
        if validation["is_valid"]:
            if word.is_valid is False:
                word.is_valid = True
            continue

        invalid_count += 1
        invalid_examples.append(
            {
                "word": word.word,
                "reason": validation["reason"] or "validation_failed",
                "suggestions": validation.get("suggestions", []),
            }
        )
        if delete_invalid:
            db.session.delete(word)
            deleted_count += 1
            continue

        if mark_word_invalid(word):
            marked_count += 1

    db.session.commit()
    invalidate_word_list_cache()
    return {
        "scanned": scanned,
        "invalid": invalid_count,
        "deleted": deleted_count,
        "marked_invalid": marked_count,
        "examples": invalid_examples[:10],
        "mode": "delete" if delete_invalid else "mark",
    }


def main():
    parser = argparse.ArgumentParser(description="Validate stored words and remove or mark invalid entries.")
    parser.add_argument("--delete", action="store_true", help="Delete invalid words instead of marking them invalid.")
    parser.add_argument("--limit", type=int, default=None, help="Only scan the first N words.")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        report = clean_invalid_words(delete_invalid=args.delete, limit=args.limit)

    print(f"Cleanup mode: {report['mode']}")
    print(f"Words scanned: {report['scanned']}")
    print(f"Invalid words found: {report['invalid']}")
    print(f"Words deleted: {report['deleted']}")
    print(f"Words marked invalid: {report['marked_invalid']}")
    if report["examples"]:
        print("Sample invalid entries:")
        for item in report["examples"]:
            suggestions = ", ".join(item["suggestions"]) if item["suggestions"] else "none"
            print(f"- {item['word']} | reason={item['reason']} | suggestions={suggestions}")


if __name__ == "__main__":
    main()
