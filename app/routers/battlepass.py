from fastapi import APIRouter, Header, HTTPException, Depends
from jose import jwt as jose_jwt
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..config import settings
from ..services.battlepass import get_progress, add_xp
from ..schemas import BattlePassProgressOut

router = APIRouter(prefix="/battlepass", tags=["battlepass"])

def user_id_from_header(authorization: str | None) -> int:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ", 1)[1]
    payload = jose_jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    return int(payload["sub"])

@router.get("/me", response_model=BattlePassProgressOut)
async def my_progress(authorization: str | None = Header(None), db: AsyncSession = Depends(get_session)):
    uid = user_id_from_header(authorization)
    prog, next_xp = await get_progress(db, uid)
    return BattlePassProgressOut(season=prog.season, current_level=prog.current_level, current_xp=prog.current_xp, next_level_xp=next_xp)

@router.post("/add_xp/{amount}", response_model=BattlePassProgressOut)
async def gain_xp(amount: int, authorization: str | None = Header(None), db: AsyncSession = Depends(get_session)):
    uid = user_id_from_header(authorization)
    prog = await add_xp(db, uid, amount)
    # compute next level req
    from sqlalchemy import select
    from ..models import BattlePass
    q = await db.execute(select(BattlePass).where(BattlePass.season==prog.season, BattlePass.level==prog.current_level+1))
    next_bp = q.scalar_one_or_none()
    next_xp = next_bp.xp_required if next_bp else 0
    return BattlePassProgressOut(season=prog.season, current_level=prog.current_level, current_xp=prog.current_xp, next_level_xp=next_xp)
