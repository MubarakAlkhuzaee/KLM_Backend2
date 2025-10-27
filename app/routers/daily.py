from fastapi import APIRouter, Depends, Query
from datetime import date as Date
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..services.words import get_daily_word
from ..schemas import DailyWordOut

router = APIRouter(prefix="/daily", tags=["daily"])

@router.get("", response_model=DailyWordOut)
async def daily_word(date: str | None = Query(default=None, description="YYYY-MM-DD (Riyadh)"),
                     db: AsyncSession = Depends(get_session)):
    d: Date | None = None
    if date:
        y, m, d_ = map(int, date.split("-"))
        from datetime import date as dtdate
        d = dtdate(y, m, d_)
    date_str, idx, word_obj = await get_daily_word(db, for_date=d)
    if isinstance(word_obj, dict):
        return DailyWordOut(date=date_str, index=idx, word=word_obj["word"], definition=word_obj["definition"])
    else:
        return DailyWordOut(date=date_str, index=idx, word=word_obj.word, definition=word_obj.definition)
