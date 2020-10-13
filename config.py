import os


class Config:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "").split())
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DB_URI = os.environ.get("DATABASE_URL")
    SESSION_NAME = os.environ.get("SESSION_NAME")
    WORKERS = 200
