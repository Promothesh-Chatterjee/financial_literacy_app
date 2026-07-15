
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import init_db
from .routers import auth, onboarding
from .routers import tokens, portfolio, market, trade
from .routers import admin_market
from .routers import daily_snapshot
from .tasks import cleanup_refresh_tokens_loop
from .config import settings

app = FastAPI(title="FinLit Sim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(init_db.router, prefix="/dev", tags=["dev"])
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(tokens.router)
app.include_router(portfolio.router)
app.include_router(market.router)
app.include_router(trade.router)
app.include_router(admin_market.router)
app.include_router(daily_snapshot.router)


@app.on_event("startup")
async def start_background_tasks():
    # start background cleanup for refresh tokens
    import asyncio
    asyncio.create_task(cleanup_refresh_tokens_loop())

