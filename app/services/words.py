import io, json, math
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_session
from ..models import DictionaryWord, DailyOverride
from ..schemas import UploadWordsResult, WordOut
from ..config import settings

router = APIRouter(prefix="/words", tags=["words"])

@router.post("/upload", response_model=UploadWordsResult)
async def upload_words(
    admin_key: str = Header(None, convert_underscores=False),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    if admin_key != settings.ADMIN_UPLOAD_KEY:
        raise HTTPException(401, "Invalid admin key")
    raw = (await file.read()).decode("utf-8")
    data = json.loads(raw)
    # Expect list of { "word": "...", "definition": "...", "source": "..."? }
    if not isinstance(data, list):
        raise HTTPException(400, "Expected a JSON list")

    inserted = 0
    for item in data:
        w = Word(word=item["word"], definition=item["definition"], source=item.get("source"))
        db.add(w)
        inserted += 1
    await db.commit()
    return UploadWordsResult(inserted=inserted)

def _days_since_start(utc_today: datetime) -> int:
    # settings.WOD_START_DATE is YYYY-MM-DD
    start = datetime.fromisoformat(settings.WOD_START_DATE).replace(tzinfo=timezone.utc)
    delta = utc_today.date() - start.date()
    return delta.days if delta.days >= 0 else 0

@router.get("/daily", response_model=WordOut)
async def daily_word(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Word.id))
    ids = [r[0] for r in res.all()]
    if not ids:
        raise HTTPException(404, "No words uploaded")
    ids.sort()
    idx = _days_since_start(datetime.now(timezone.utc)) % len(ids)
    word_id = ids[idx]

    res = await db.execute(select(Word).where(Word.id == word_id))
    w = res.scalar_one()
    return WordOut(id=w.id, word=w.word, definition=w.definition, source=w.source)
