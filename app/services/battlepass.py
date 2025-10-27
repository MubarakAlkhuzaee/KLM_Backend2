from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import BattlePass, UserBattlePass
from ..config import settings

async def get_progress(db: AsyncSession, user_id: int):
    q = await db.execute(select(UserBattlePass).where(UserBattlePass.user_id == user_id))
    prog = q.scalar_one_or_none()
    if not prog:
        prog = UserBattlePass(user_id=user_id, season=settings.BATTLEPASS_DEFAULT_SEASON, current_level=1, current_xp=0)
        db.add(prog)
        await db.commit()
        await db.refresh(prog)
    next_level = prog.current_level + 1
    req_q = await db.execute(select(BattlePass).where(BattlePass.season==prog.season, BattlePass.level==next_level))
    bp_next = req_q.scalar_one_or_none()
    next_xp = bp_next.xp_required if bp_next else 0
    return prog, next_xp

async def add_xp(db: AsyncSession, user_id: int, amount: int):
    prog, _ = await get_progress(db, user_id)
    prog.current_xp += amount
    # Level up loop
    while True:
        next_level = prog.current_level + 1
        q = await db.execute(select(BattlePass).where(BattlePass.season==prog.season, BattlePass.level==next_level))
        bp_next = q.scalar_one_or_none()
        if not bp_next: break
        if prog.current_xp >= bp_next.xp_required:
            prog.current_level = next_level
        else:
            break
    await db.commit()
    await db.refresh(prog)
    return prog
