import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "9238080376:AAGEC1u-Uo6NUuAmPHz-OzA_RvQHmu2nxBA"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///secretary.db")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

raw_ids = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "9276371328")
ALLOWED_USER_IDS = [
    int(uid.strip())
    for uid in raw_ids.split(",")
    if uid.strip().isdigit()
]