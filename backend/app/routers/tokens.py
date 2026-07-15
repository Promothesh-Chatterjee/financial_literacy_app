from fastapi import APIRouter, Response, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..security import create_refresh_token, decode_token, create_csrf_token
from ..models import RefreshToken
from datetime import datetime
from ..deps import get_session
from sqlalchemy import select, update, insert

router = APIRouter(prefix="/token", tags=["token"])


@router.post("/refresh")
async def refresh(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    # expect refresh_token cookie and csrf header
    refresh_token = request.cookies.get("refresh_token")
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("x-csrf-token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    if csrf_cookie != csrf_header:
        raise HTTPException(status_code=403, detail="CSRF token missing or mismatch")

    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jti = payload.get("jti")
    user_id = int(payload.get("sub"))
    if not jti or not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh payload")

    # validate stored refresh token
    q = await session.execute(select(RefreshToken).where(RefreshToken.token_jti == jti))
    rt = q.scalars().first()
    if not rt or rt.revoked or (rt.expires_at and rt.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")

    # rotate refresh token: revoke old and create new
    await session.execute(update(RefreshToken).where(RefreshToken.token_jti == jti).values(revoked=True))
    new_token, new_jti, new_expires = create_refresh_token(subject=str(user_id), expires_days=7)
    await session.execute(insert(RefreshToken).values(token_jti=new_jti, user_id=user_id, expires_at=new_expires, revoked=False))
    await session.commit()

    # create new access token (short-lived)
    from ..security import create_access_token
    access_token = create_access_token(subject=str(user_id), expires_delta=datetime.utcnow() - datetime.utcnow())
    # (above line uses zero delta; instead issue 15 minutes)
    from datetime import timedelta
    access_token = create_access_token(subject=str(user_id), expires_delta=timedelta(minutes=15))

    # set cookies
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", max_age=15 * 60)
    response.set_cookie(key="refresh_token", value=new_token, httponly=True, samesite="lax", max_age=7 * 24 * 3600)
    new_csrf = create_csrf_token()
    response.set_cookie(key="csrf_token", value=new_csrf, httponly=False, samesite="lax", max_age=7 * 24 * 3600)

    return {"access_token": access_token}
