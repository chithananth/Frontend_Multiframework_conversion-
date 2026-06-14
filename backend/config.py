import os
from urllib.parse import quote_plus

class Config:
    # ── MySQL ──────────────────────────────────────────────
    MYSQL_USER     = os.getenv("DB_USER",     "root")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "Chitha@123")
    MYSQL_HOST     = os.getenv("DB_HOST",     "localhost")
    MYSQL_PORT     = os.getenv("DB_PORT",     "3306")
    MYSQL_DB       = os.getenv("DB_NAME",     "converter_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── General ────────────────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG       = os.getenv("FLASK_DEBUG", "1") == "1"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
