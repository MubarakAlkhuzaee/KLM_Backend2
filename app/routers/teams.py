from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import Team, User
from ..schemas import TeamOut

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("", response_model=list[TeamOut])
async def list_teams(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Team))
    return [TeamOut(code=t.code, name=t.name) for t in res.scalars().all()]

@router.post("/choose/{team_code}")
async def choose_team(team_code: str,
                      authorization: str | None = Header(None),
                      db: AsyncSession = Depends(get_session)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ", 1)[1]
    from jose import jwt as jose_jwt
    from ..config import settings
    payload = jose_jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    user_id = int(payload["sub"])

    team = (await db.execute(select(Team).where(Team.code == team_code))).scalar_one_or_none()
    if not team:
        raise HTTPException(400, "Invalid team code")
    user = await db.get(User, user_id)
    user.team_id = team.id
    await db.commit()
    return {"ok": True, "team_code": team.code}
