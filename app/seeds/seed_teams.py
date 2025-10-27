import asyncio
from sqlalchemy import select
from app.db import AsyncSessionLocal, engine
from app.models import Team, Base

TEAMS = [
    ("T01", "Team Falcon"),
    ("T02", "Team Oasis"),
    ("T03", "Team Dune"),
    ("T04", "Team Crescent"),
    ("T05", "Team Palm"),
    ("T06", "Team Mirage"),
    ("T07", "Team Sandstorm"),
    ("T08", "Team Desert Rose"),
    ("T09", "Team Caravan"),
    ("T10", "Team Minaret"),
    ("T11", "Team Date"),
    ("T12", "Team Saffron"),
    ("T13", "Team Spice"),
]

async def main():
    async with AsyncSessionLocal() as db:
        for code, name in TEAMS:
            q = await db.execute(select(Team).where(Team.code == code))
            if not q.scalar_one_or_none():
                db.add(Team(code=code, name=name))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(main())
