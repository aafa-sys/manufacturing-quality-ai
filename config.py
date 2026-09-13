import os
from pathlib import Path
from dotenv import load_dotenv

# Cari file .env di folder yang sama dengan config.py
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "masystem"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
