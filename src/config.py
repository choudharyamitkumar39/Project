import os

TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))
DB_PATH = os.getenv("DB_PATH", "devices.db")
