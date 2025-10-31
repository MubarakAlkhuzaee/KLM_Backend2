from zoneinfo import ZoneInfo
from datetime import datetime, date
from .config import settings

def riyadh_today() -> date:
    tz = ZoneInfo(settings.TIMEZONE)
    return datetime.now(tz).date()

def date_key(d: date | None = None) -> str:
    d = d or riyadh_today()
    return d.isoformat()
