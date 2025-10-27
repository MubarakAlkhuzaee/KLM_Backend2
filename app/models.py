from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, JSON, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))

    users = relationship("User", back_populates="team")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)  # None for OAuth-only
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    google_sub: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)  # Google user id

    team = relationship("Team", back_populates="users")
    battle_pass = relationship("UserBattlePass", back_populates="user", uselist=False)

class DictionaryWord(Base):
    __tablename__ = "dictionary_words"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(128), index=True)         # with tashkeel if you want
    definition: Mapped[str] = mapped_column(Text)
    # Optional metadata (source, root, rarity, etc.)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class DailyOverride(Base):
    """
    Optional: if you ever want to force a specific word on a specific date.
    """
    __tablename__ = "daily_overrides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_key: Mapped[str] = mapped_column(String(10), unique=True, index=True)  # YYYY-MM-DD (Riyadh)
    dictionary_word_id: Mapped[int] = mapped_column(ForeignKey("dictionary_words.id"))
    word = relationship("DictionaryWord")

class BattlePass(Base):
    __tablename__ = "battle_pass"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[str] = mapped_column(String(32), index=True)  # e.g., "S1"
    level: Mapped[int] = mapped_column(Integer)                  # 1..N
    xp_required: Mapped[int] = mapped_column(Integer)            # cumulative or per-level
    reward: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint("season", "level", name="uix_season_level"),)

class UserBattlePass(Base):
    __tablename__ = "user_battle_pass"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    season: Mapped[str] = mapped_column(String(32))
    current_level: Mapped[int] = mapped_column(Integer, default=1)
    current_xp: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="battle_pass")
