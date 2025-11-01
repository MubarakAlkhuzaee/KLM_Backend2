from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # bcrypt has a 72-byte limit, truncate if necessary
    p_bytes = p.encode('utf-8')
    if len(p_bytes) > 72:
        p_bytes = p_bytes[:72]
        p = p_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    # Truncate to 72 bytes for verification (must match hash_password behavior)
    p_bytes = p.encode('utf-8')
    if len(p_bytes) > 72:
        p_bytes = p_bytes[:72]
        p = p_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(p, hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
