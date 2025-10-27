from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str] = None
    team_code: Optional[str] = None
    class Config: from_attributes = True

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None
    team_code: Optional[str] = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthStartOut(BaseModel):
    authorization_url: str

class TeamOut(BaseModel):
    code: str
    name: str

class DailyWordOut(BaseModel):
    date: str            # YYYY-MM-DD (Riyadh)
    index: int           # selected index
    word: str
    definition: str

class BattlePassProgressOut(BaseModel):
    season: str
    current_level: int
    current_xp: int
    next_level_xp: int
