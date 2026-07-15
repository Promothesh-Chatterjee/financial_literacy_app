from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import User
from ..schemas import UserCreate, Token
from ..security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from ..deps import get_current_user
from ..security import create_refresh_token, create_csrf_token, decode_token
from ..models import RefreshToken
from datetime import datetime
from sqlalchemy import insert, select, update


router = APIRouter(prefix="/auth", tags=["auth"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/signup", response_model=Token)
async def signup(payload: UserCreate, response: Response, session: AsyncSession = Depends(get_session)):
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    # create tokens and set cookies similar to login
    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=15))
    refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id), expires_days=7)
    await session.execute(insert(RefreshToken).values(token_jti=jti, user_id=user.id, expires_at=expires_at, revoked=False))
    await session.commit()
    csrf = create_csrf_token()
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", max_age=15 * 60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", max_age=7 * 24 * 3600)
    response.set_cookie(key="csrf_token", value=csrf, httponly=False, samesite="lax", max_age=7 * 24 * 3600)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(User).where(User.email == form_data.username))
    user = q.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    # create access token (short-lived) and refresh token
    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=15))
    refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id), expires_days=7)

    # persist refresh token
    await session.execute(insert(RefreshToken).values(token_jti=jti, user_id=user.id, expires_at=expires_at, revoked=False))
    await session.commit()

    # create csrf token for double-submit
    csrf = create_csrf_token()

    # Set cookies: access_token (httpOnly), refresh_token (httpOnly), csrf_token (accessible to JS)
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", max_age=15 * 60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", max_age=7 * 24 * 3600)
    response.set_cookie(key="csrf_token", value=csrf, httponly=False, samesite="lax", max_age=7 * 24 * 3600)

    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/logout")
async def logout(response: Response, request: Request):
    token = request.cookies.get("refresh_token")
    if token:
        try:
            data = decode_token(token)
            jti = data.get("jti")
            if jti:
                async with AsyncSessionLocal() as s:
                    await s.execute(update(RefreshToken).where(RefreshToken.token_jti == jti).values(revoked=True))
                    await s.commit()
        except Exception:
            pass

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return {"status": "ok"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}
