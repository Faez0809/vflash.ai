import os

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("FLASK_DEBUG", "1")
os.environ.setdefault("SEND_FILE_MAX_AGE_DEFAULT", "0")
os.environ.setdefault("TEMPLATES_AUTO_RELOAD", "1")
os.environ.setdefault("VFLASH_LOCAL_DEV", "1")

from app import create_app

app = create_app()


if __name__ == "__main__":
    print("Serving updated Vocabai app from:", os.path.abspath(__file__))
    print("Open: http://127.0.0.1:5000")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "1").lower() in {"1", "true", "yes"},
        use_reloader=False,
    )
