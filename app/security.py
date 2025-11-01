from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import hashlib
from .config import settings

# Use plain bcrypt, but we'll SHA256 hash passwords first manually
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Hash password with SHA256 first (produces 64 bytes, always under 72-byte limit)
    # This is what bcrypt_sha256 does internally, but we'll do it explicitly to avoid issues
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(sha256_hash)

def verify_password(plain_password: str, hashed: str) -> bool:
    # Hash the plain password with SHA256 to match what hash_password does
    sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(sha256_hash, hashed)

def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
