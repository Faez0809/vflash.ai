import csv
import os

import runtime_compat
from dotenv import load_dotenv
from flask import Flask

from models import MasterWord, db


load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
LOCAL_DB_PATH = r"C:\vocabai\vocabai.db"
os.makedirs(INSTANCE_DIR, exist_ok=True)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{LOCAL_DB_PATH}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def import_words():
    inserted_count = 0
    with app.app_context():
        db.create_all()
        csv_path = os.path.join(BASE_DIR, "words.csv")
        with open(csv_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                word = (row.get("word") or "").strip().lower()
                difficulty = (row.get("difficulty") or "").strip().lower()
                if not word or difficulty not in {"beginner", "medium", "hard"}:
                    continue

                existing = MasterWord.query.filter_by(word=word).first()
                if existing:
                    continue

                db.session.add(MasterWord(word=word, difficulty=difficulty))
                inserted_count += 1

        db.session.commit()
        print(f"Imported {inserted_count} master words.")


if __name__ == "__main__":
    import_words()
