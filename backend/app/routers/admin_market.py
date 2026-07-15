from fastapi import APIRouter, HTTPException
from typing import List
from ..db import AsyncSessionLocal
from ..models import NSEHoliday
from sqlalchemy import insert
from datetime import datetime
from ..config import settings

router = APIRouter(prefix="/market/admin", tags=["market-admin"])


@router.post("/seed-holidays")
async def seed_holidays(items: List[dict]):
    """Seed holidays. Each item: {date: 'YYYY-MM-DD', name: 'Holiday Name'}
    This endpoint is gated by ALLOW_DEV_INIT to avoid misuse in production.
    """
    if not settings.allow_dev_init:
        raise HTTPException(status_code=403, detail="Seeding disabled")
    async with AsyncSessionLocal() as session:
        for it in items:
            dt = datetime.fromisoformat(it.get("date"))
            name = it.get("name")
            await session.execute(insert(NSEHoliday).values(date=dt, name=name))
        await session.commit()
    return {"status": "ok", "inserted": len(items)}
