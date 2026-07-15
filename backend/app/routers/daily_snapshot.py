from fastapi import APIRouter, Header, HTTPException, Depends
from ..config import settings
from ..db import AsyncSessionLocal
from ..models import DailyMarketSnapshot
from sqlalchemy import insert
from datetime import datetime

router = APIRouter(prefix="/market", tags=["market"])


@router.post("/daily_snapshot")
async def receive_snapshot(payload: dict, x_market_secret: str | None = Header(None)):
    # simple shared-secret header authentication for worker
    if not settings.market_worker_secret or x_market_secret != settings.market_worker_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # payload expected: { date: 'YYYY-MM-DD', index_name: 'NIFTY', open, high, low, close, metadata }
    date_str = payload.get('date')
    if not date_str:
        raise HTTPException(status_code=400, detail="missing date")
    dt = datetime.fromisoformat(date_str)
    async with AsyncSessionLocal() as session:
        await session.execute(insert(DailyMarketSnapshot).values(
            date=dt,
            index_name=payload.get('index_name'),
            open=payload.get('open'),
            high=payload.get('high'),
            low=payload.get('low'),
            close=payload.get('close'),
            metadata=payload.get('metadata', {})
        ))
        await session.commit()
    return {"status": "ok"}
