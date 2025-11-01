from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, daily, battlepass, teams
from .db import engine, AsyncSessionLocal
from .models import Base, Team, DictionaryWord, BattlePass
from sqlalchemy import select
import json
from pathlib import Path


app = FastAPI(title="Arabic Wordle Backend")

# CORS for Godot web export or local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(daily.router, prefix="/api")
app.include_router(battlepass.router, prefix="/api")
app.include_router(teams.router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    try:
        # Ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Seed teams, battle pass, and words if empty
        async with AsyncSessionLocal() as db:
            # Teams (13)
            res = await db.execute(select(Team.id))
            if not res.first():
                teams_data = [
                    ("T01", "Team Falcon"), ("T02", "Team Oasis"), ("T03", "Team Dune"),
                    ("T04", "Team Crescent"), ("T05", "Team Palm"), ("T06", "Team Mirage"),
                    ("T07", "Team Sandstorm"), ("T08", "Team Desert Rose"), ("T09", "Team Caravan"),
                    ("T10", "Team Minaret"), ("T11", "Team Date"), ("T12", "Team Saffron"), ("T13", "Team Spice"),
                ]
                for code, name in teams_data:
                    db.add(Team(code=code, name=name))
                await db.commit()
                print("✓ Teams seeded")

            # Battle pass basic season S1 levels (1..10)
            res_bp = await db.execute(select(BattlePass.id))
            if not res_bp.first():
                for level in range(1, 11):
                    # cumulative xp requirements (e.g., 100, 300, 600, ...)
                    xp_required = level * (level + 1) * 50 // 2
                    db.add(BattlePass(season="S1", level=level, xp_required=xp_required, reward=None))
                await db.commit()
                print("✓ Battle pass seeded")

            # Words from bundled JSON if table empty
            res_w = await db.execute(select(DictionaryWord.id))
            if not res_w.first():
                data_path = Path(__file__).parent / "data" / "arabic_100_with_roots_with_source.json"
                if data_path.exists():
                    items = json.loads(data_path.read_text(encoding="utf-8"))
                    for item in items:
                        meta = {"root": item.get("root"), "source": item.get("source")}
                        db.add(DictionaryWord(word=item.get("word"), definition=item.get("definition"), meta=meta))
                    await db.commit()
                    print(f"✓ {len(items)} words seeded")
                else:
                    print(f"⚠ Words file not found: {data_path}")
    except Exception as e:
        import traceback
        print(f"⚠ Startup error: {e}")
        print(traceback.format_exc())

@app.get("/health")
async def health():
    return {"ok": True}
