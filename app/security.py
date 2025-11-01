from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt
import hashlib
from .config import settings

def hash_password(password: str) -> str:
    # Hash password with SHA256 first (produces 64 bytes hex string, always under 72-byte limit)
    # Then bcrypt the SHA256 hash to avoid any length issues
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # bcrypt.hashpw expects bytes, and rounds=12 is a good default
    hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed: str) -> bool:
    # Hash the plain password with SHA256 to match what hash_password does
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    # bcrypt.checkpw expects bytes
    return bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
