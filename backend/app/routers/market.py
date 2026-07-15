from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import NSEHoliday, DailyMarketSnapshot
from sqlalchemy import select
from datetime import datetime
from ..cache import get_redis
import json

router = APIRouter(prefix="/market", tags=["market"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/holiday")
async def check_holiday(date: str, session: AsyncSession = Depends(get_session)):
    # date expected YYYY-MM-DD
    dt = datetime.fromisoformat(date)
    q = await session.execute(select(NSEHoliday).where(NSEHoliday.date == dt))
    h = q.scalars().first()
    if h:
        return {"closed": True, "reason": h.name}
    if dt.weekday() >= 5:
        return {"closed": True, "reason": "Weekend"}
    return {"closed": False}


@router.get("/quote")
async def quote(ticker: str = Query(...), session: AsyncSession = Depends(get_session)):
    redis = await get_redis()
    if redis is not None:
        key = f"market:prices:{ticker}"
        raw = await redis.get(key)
        if raw:
            return json.loads(raw)

    today = datetime.utcnow().date()
    q = await session.execute(
        select(DailyMarketSnapshot)
        .where(DailyMarketSnapshot.index_name == ticker, DailyMarketSnapshot.date == today)
    )
    snapshot = q.scalars().first()
    if snapshot:
        payload = snapshot.payload or {}
        price = payload.get("price") or payload.get("close")
        return {"ticker": ticker, "price": float(price) if price is not None else None, "source": "snapshot", "payload": payload}

    raise HTTPException(status_code=404, detail="Price unavailable")


@router.get("/indices")
async def indices(session: AsyncSession = Depends(get_session)):
    redis = await get_redis()
    if redis is not None:
        raw = await redis.get("market:latest")
        if raw:
            return json.loads(raw)

    q = await session.execute(
        select(DailyMarketSnapshot)
        .where(DailyMarketSnapshot.index_name.in_(["NIFTY", "SENSEX"]))
        .order_by(DailyMarketSnapshot.date.desc())
        .limit(2)
    )
    snapshots = q.scalars().all()
    data = []
    for snap in snapshots:
        payload = snap.payload or {}
        price = payload.get("price") or float(snap.close) if snap.close is not None else None
        data.append({"index_name": snap.index_name, "date": snap.date.isoformat(), "price": float(price) if price is not None else None, "source": "snapshot"})
    return {"indices": data}
