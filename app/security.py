from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.hash import bcrypt_sha256
from .config import settings

def hash_password(password: str) -> str:
    return bcrypt_sha256.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return bcrypt_sha256.verify(plain_password, hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
