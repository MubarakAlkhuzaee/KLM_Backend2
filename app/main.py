from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, daily, battlepass, teams
from .db import engine


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

@app.get("/health")
async def health():
    return {"ok": True}
