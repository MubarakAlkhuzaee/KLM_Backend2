from fastapi import APIRouter, Header, HTTPException, Depends
from jose import jwt as jose_jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..config import settings
from ..models import User, Team
from ..schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
async def me(authorization: str | None = Header(None), db: AsyncSession = Depends(get_session)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ", 1)[1]
    payload = jose_jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    user = await db.get(User, int(payload["sub"]))
    team_code = None
    if user.team_id:
        t = await db.get(Team, user.team_id)
        team_code = t.code
    return UserOut(id=user.id, email=user.email, display_name=user.display_name, team_code=team_code)
