from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import NSEHoliday
from sqlalchemy import select
from datetime import datetime

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
    # weekend
    if dt.weekday() >= 5:
        return {"closed": True, "reason": "Weekend"}
    return {"closed": False}
