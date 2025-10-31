import json
from pathlib import Path
from datetime import datetime, date
from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import DictionaryWord, DailyOverride
from ..config import settings

_WORDS_CACHE: list[dict] | None = None
_WORDS_PATH = Path(__file__).parent.parent / "data" / "arabic_100_with_roots_with_source.json"

def _load_words_file() -> list[dict]:
    global _WORDS_CACHE
    if _WORDS_CACHE is None:
        raw = _WORDS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        # Normalize to {word, definition, meta}
        normalized = []
        for item in data:
            normalized.append({
                "word": item.get("word"),
                "definition": item.get("definition"),
                "meta": {"root": item.get("root"), "source": item.get("source")},
            })
        _WORDS_CACHE = normalized
    return _WORDS_CACHE

def _riyadh_date(d: date | None = None) -> date:
    if d is not None:
        return d
    tz = ZoneInfo(settings.TIMEZONE)
    return datetime.now(tz).date()

def _index_for_date(d: date, total: int) -> int:
    # Deterministic rotation from a fixed epoch
    epoch = date(2025, 1, 1)
    return ((d - epoch).days) % total

async def get_daily_word(db: AsyncSession, for_date: date | None = None):
    d = _riyadh_date(for_date)
    # Overrides take precedence
    ov = await db.execute(select(DailyOverride).where(DailyOverride.date_key == d.isoformat()))
    override = ov.scalar_one_or_none()
    if override:
        w = await db.get(DictionaryWord, override.dictionary_word_id)
        return d.isoformat(), -1, w

    # Try DB words first
    all_ids_res = await db.execute(select(DictionaryWord.id))
    ids = [row[0] for row in all_ids_res.all()]
    if ids:
        idx = _index_for_date(d, len(ids))
        w = await db.get(DictionaryWord, ids[idx])
        return d.isoformat(), idx, w

    # Fallback to bundled JSON
    words = _load_words_file()
    idx = _index_for_date(d, len(words))
    return d.isoformat(), idx, words[idx]
