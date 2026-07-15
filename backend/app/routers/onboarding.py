from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import UserProfile, VirtualWallet, User
from ..schemas import OnboardingData
from ..deps import get_current_user, get_session, verify_csrf

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/complete")
async def complete_onboarding(data: OnboardingData, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session), csrf_ok: bool = Depends(verify_csrf)):
    # create or update profile
    profile = UserProfile(user_id=user.id, full_name=data.full_name, employment_status=data.employment_status,
                          annual_salary=data.annual_salary, objectives=data.objectives, risk_profile=data.risk_profile)
    session.add(profile)
    # seed virtual wallet
    wallet = VirtualWallet(user_id=user.id, cash_balance=data.starting_capital)
    session.add(wallet)
    await session.commit()
    return {"status": "ok"}
