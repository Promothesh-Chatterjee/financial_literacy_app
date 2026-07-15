from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .config import settings
from .db import AsyncSessionLocal
from sqlalchemy import select
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    # Prefer cookie token if present
    token_value = None
    if request.cookies.get("access_token"):
        token_value = request.cookies.get("access_token")
    elif token:
        token_value = token

    if not token_value:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token_value, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def verify_csrf(request: Request):
    # double-submit: header x-csrf-token must match csrf_token cookie
    cookie = request.cookies.get("csrf_token")
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or cookie != header:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    return True
