from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import VirtualWallet, Holding, Transaction, DailyMarketSnapshot
from ..deps import get_current_user, get_session, verify_csrf
from ..schemas import TradeOrder
from ..cache import get_redis
from datetime import datetime
import json

router = APIRouter(prefix="/trade", tags=["trade"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def resolve_market_price(ticker: str, session: AsyncSession):
    redis = await get_redis()
    if redis is not None:
        key = f"market:prices:{ticker}"
        raw = await redis.get(key)
        if raw:
            payload = json.loads(raw)
            price = payload.get("price")
            if price is not None:
                return float(price)

    today = datetime.utcnow().date()
    q = await session.execute(
        select(DailyMarketSnapshot).where(
            DailyMarketSnapshot.index_name == ticker,
            DailyMarketSnapshot.date == today,
        )
    )
    snapshot = q.scalars().first()
    if snapshot:
        payload = snapshot.payload or {}
        price = payload.get("price") or payload.get("close")
        if price is not None:
            return float(price)

    raise HTTPException(status_code=404, detail="Market price unavailable")


@router.post("/order")
async def place_order(order: TradeOrder, user=Depends(get_current_user), session: AsyncSession = Depends(get_session), csrf_ok: bool = Depends(verify_csrf)):
    ticker = order.ticker.strip().upper()
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    q = await session.execute(select(VirtualWallet).where(VirtualWallet.user_id == user.id))
    wallet = q.scalars().first()
    if not wallet:
        raise HTTPException(status_code=400, detail="Virtual wallet not found")

    price = float(order.price) if order.price is not None else await resolve_market_price(ticker, session)
    total_amount = round(order.quantity * price, 2)

    q = await session.execute(select(Holding).where(Holding.user_id == user.id, Holding.ticker == ticker))
    holding = q.scalars().first()

    if order.action == "BUY":
        if float(wallet.cash_balance) < total_amount:
            raise HTTPException(status_code=400, detail="Insufficient cash balance")

        wallet.cash_balance = float(wallet.cash_balance) - total_amount
        if holding:
            existing_qty = float(holding.quantity)
            new_qty = existing_qty + order.quantity
            avg_cost = float(holding.avg_price)
            holding.avg_price = (existing_qty * avg_cost + total_amount) / new_qty
            holding.quantity = new_qty
        else:
            holding = Holding(user_id=user.id, ticker=ticker, quantity=order.quantity, avg_price=price)
            session.add(holding)

    elif order.action == "SELL":
        if not holding or float(holding.quantity) < order.quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

        wallet.cash_balance = float(wallet.cash_balance) + total_amount
        holding.quantity = float(holding.quantity) - order.quantity
        if float(holding.quantity) == 0:
            holding.avg_price = 0
        session.add(holding)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    transaction = Transaction(
        user_id=user.id,
        ticker=ticker,
        action=order.action,
        quantity=order.quantity,
        price=price,
        fees=0,
        payload={"source": "trade"},
    )
    session.add(transaction)
    session.add(wallet)
    await session.commit()

    return {
        "status": "ok",
        "ticker": ticker,
        "action": order.action,
        "quantity": order.quantity,
        "price": price,
        "cash_balance": float(wallet.cash_balance),
    }
