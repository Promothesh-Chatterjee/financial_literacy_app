from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from .config import settings
import uuid

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(settings.access_token_expire_minutes))
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str, expires_days: int = 7) -> (str, str, datetime):
    # returns (token, jti, expires_at)
    jti = uuid.uuid4().hex
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode = {"sub": str(subject), "jti": jti, "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


def create_csrf_token() -> str:
    return uuid.uuid4().hex
