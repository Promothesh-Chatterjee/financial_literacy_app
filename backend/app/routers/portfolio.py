from fastapi import APIRouter, Depends
from ..deps import get_current_user, get_session
from sqlalchemy import select
from ..models import VirtualWallet, Holding
from sqlalchemy.ext.asyncio import AsyncSession
from ..cache import get_redis
import json

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary")
async def summary(user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    # compute simple net worth using avg_price as placeholder for market price
    q = await session.execute(select(VirtualWallet).where(VirtualWallet.user_id == user.id))
    wallet = q.scalars().first()
    cash = float(wallet.cash_balance) if wallet else 0.0

    q2 = await session.execute(select(Holding).where(Holding.user_id == user.id))
    holdings = q2.scalars().all()
    total_holdings = 0.0
    items = []
    # attempt to fetch live prices from Redis (key: market:prices:<TICKER>)
    redis = await get_redis()
    for h in holdings:
        qty = float(h.quantity)
        avg_price = float(h.avg_price)
        current_price = avg_price
        try:
            if redis is not None:
                key = f"market:prices:{h.ticker}"
                raw = await redis.get(key)
                if raw:
                    parsed = json.loads(raw)
                    # expected format: { price: number, fetched_at: iso }
                    current_price = float(parsed.get('price', avg_price))
        except Exception:
            # on any redis error, fallback to avg_price
            current_price = avg_price

        val = qty * current_price
        pnl = (current_price - avg_price) * qty
        total_holdings += val
        items.append({"ticker": h.ticker, "quantity": qty, "avg_price": avg_price, "current_price": current_price, "value": val, "unrealized_pnl": pnl})

    net_worth = cash + total_holdings
    todays_pnl = sum([it.get('unrealized_pnl', 0.0) for it in items])

    return {"cash": cash, "holdings_value": total_holdings, "net_worth": net_worth, "holdings": items, "todays_pnl": todays_pnl}
