import asyncio
from datetime import datetime, timedelta
from sqlalchemy import delete, select
from .db import AsyncSessionLocal
from .models import RefreshToken


async def cleanup_refresh_tokens_loop(interval_seconds: int = 3600):
    """Background task to purge expired refresh tokens and old revoked tokens."""
    while True:
        try:
            async with AsyncSessionLocal() as session:
                now = datetime.utcnow()
                # delete tokens that expired more than 1 day ago
                await session.execute(delete(RefreshToken).where(RefreshToken.expires_at < now))
                # optionally delete revoked tokens older than 30 days
                cutoff = now - timedelta(days=30)
                await session.execute(delete(RefreshToken).where(RefreshToken.revoked == True, RefreshToken.expires_at < cutoff))
                await session.commit()
        except Exception:
            # swallow exceptions to keep loop alive; logging can be added
            pass
        await asyncio.sleep(interval_seconds)
