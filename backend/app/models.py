from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


def now():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    wallet = relationship("VirtualWallet", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255))
    employment_status = Column(String(50))
    annual_salary = Column(Numeric(14, 2))
    objectives = Column(JSON)
    risk_profile = Column(String(50))
    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="profile")


class VirtualWallet(Base):
    __tablename__ = "virtual_wallet"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    cash_balance = Column(Numeric(20, 2), default=0)
    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="wallet")


class VirtualBankAccount(Base):
    __tablename__ = "virtual_bank_accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_name = Column(String(255))
    balance = Column(Numeric(20, 2), default=0)
    interest_rate = Column(Numeric(5, 4), default=0)
    created_at = Column(DateTime, default=now)


class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(50), nullable=False, index=True)
    quantity = Column(Numeric(20, 4), default=0)
    avg_price = Column(Numeric(20, 4), default=0)
    created_at = Column(DateTime, default=now)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(50), nullable=True)
    action = Column(String(10))  # BUY / SELL / DEPOSIT / WITHDRAW
    quantity = Column(Numeric(20, 4), default=0)
    price = Column(Numeric(20, 4), default=0)
    fees = Column(Numeric(20, 4), default=0)
    payload = Column(JSON)
    created_at = Column(DateTime, default=now)


class ScoreLog(Base):
    __tablename__ = "score_log"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer)
    reason = Column(Text)
    created_at = Column(DateTime, default=now)


class DailyMarketSnapshot(Base):
    __tablename__ = "daily_market_snapshot"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    index_name = Column(String(50))
    open = Column(Numeric(20, 4))
    high = Column(Numeric(20, 4))
    low = Column(Numeric(20, 4))
    close = Column(Numeric(20, 4))
    payload = Column(JSON)


class NewsFeedCache(Base):
    __tablename__ = "news_feed_cache"
    id = Column(Integer, primary_key=True)
    fetched_at = Column(DateTime, default=now)
    query = Column(String(255))
    payload = Column(JSON)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    token_jti = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)


class NSEHoliday(Base):
    __tablename__ = "nse_holidays"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=now)
