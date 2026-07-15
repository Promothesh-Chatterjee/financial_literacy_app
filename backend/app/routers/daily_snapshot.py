from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..db import AsyncSessionLocal
from ..models import DailyMarketSnapshot
from datetime import datetime

router = APIRouter(prefix="/market", tags=["market"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/daily_snapshot")
async def receive_snapshot(payload: dict, x_market_secret: str | None = Header(None)):
    if not settings.market_worker_secret or x_market_secret != settings.market_worker_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")

    date_str = payload.get("date")
    index_name = payload.get("index_name")
    if not date_str or not index_name:
        raise HTTPException(status_code=400, detail="missing date or index_name")

    try:
        dt = datetime.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid date") from exc

    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(DailyMarketSnapshot).where(
                DailyMarketSnapshot.date == dt,
                DailyMarketSnapshot.index_name == index_name,
            )
        )
        row = existing.scalars().first()
        data = {
            "date": dt,
            "index_name": index_name,
            "open": payload.get("open"),
            "high": payload.get("high"),
            "low": payload.get("low"),
            "close": payload.get("close"),
            "payload": payload.get("metadata", {}),
        }
        if row is None:
            await session.execute(insert(DailyMarketSnapshot).values(**data))
        else:
            await session.execute(update(DailyMarketSnapshot).where(DailyMarketSnapshot.id == row.id).values(**data))
        await session.commit()

    return {"status": "ok", "index_name": index_name, "date": date_str}
