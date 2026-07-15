from fastapi import APIRouter, HTTPException
from ..db import engine, Base

router = APIRouter()


@router.post("/init-db")
async def init_db():
    # Protected development-only: create all tables
    from ..config import settings
    if not settings.allow_dev_init:
        raise HTTPException(status_code=403, detail="Dev init disabled. Set ALLOW_DEV_INIT=true to enable locally.")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "detail": "tables created"}
