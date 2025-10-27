import json
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..models import DictionaryWord, DailyOverride

# Load the static JSON once at startup (also seeded into DB via migration or script)
WORDS_CACHE = None
WORDS_PATH = Path(__file__).parent.parent / "data" / "words.json"

def load_words():
    global WORDS_CACHE
    if WORDS_CACHE is None:
        WORDS_CACHE = json.loads(WORDS_PATH.read_text(encoding="utf-8"))
        # Expect [{"word": "...", "definition": "...", "meta": {...}} ...]
    return WORDS_CACHE

def riyadh_today() -> date:
    tz = ZoneInfo(settings.TIMEZONE)
    return datetime.now(tz).date()

def date_key(d: date | None = None) -> str:
    d = d or riyadh_today()
    return d.isoformat()

def index_for_date(d: date, total: int) -> int:
    # Example: cycle deterministically by days since a fixed epoch
    epoch = date(2025, 1, 1)
    delta = (d - epoch).days
    return delta % total

async def get_daily_word(db: AsyncSession, for_date: date | None = None):
    d = for_date or riyadh_today()
    # Check override first
    res = await db.execute(select(DailyOverride).where(DailyOverride.date_key == d.isoformat()))
    override = res.scalar_one_or_none()
    if override:
        word = await db.get(DictionaryWord, override.dictionary_word_id)
        return d.isoformat(), -1, word  # -1 indicates override

    # Else deterministic by index from DB count
    count_res = await db.execute(select(DictionaryWord.id))
    ids = [x[0] for x in count_res.all()]
    if not ids:
        # Fallback to in-memory json if DB empty
        words = load_words()
        idx = index_for_date(d, len(words))
        w = words[idx]
        return d.isoformat(), idx, w

    # Using DB (stable order by id)
    idx = index_for_date(d, len(ids))
    word = await db.get(DictionaryWord, ids[idx])
    return d.isoformat(), idx, word
