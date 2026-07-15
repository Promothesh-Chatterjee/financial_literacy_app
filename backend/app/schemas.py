from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OnboardingData(BaseModel):
    full_name: str
    employment_status: str
    annual_salary: Optional[float]
    objectives: List[str]
    risk_profile: str
    starting_capital: float


class TradeOrder(BaseModel):
    ticker: str
    action: Literal["BUY", "SELL"]
    quantity: float
    price: Optional[float] = None
