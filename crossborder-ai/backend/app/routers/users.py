"""VeyaShip - User Management Routes.

Credits query and deduction endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/users", tags=["Users"])


class DeductCreditsRequest(BaseModel):
    amount: int = Field(..., ge=1, description="扣减积分数")


@router.get("/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """Return the current user's credit balance."""
    return {
        "credits": current_user.credits,
    }


@router.post("/credits/deduct")
async def deduct_credits(
    payload: DeductCreditsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deduct credits atomically.

    Uses row-level locking to prevent race conditions.
    Returns 400 if credits are insufficient.
    """
    try:
        remaining = await current_user.deduct_credits(db, payload.amount)
        await db.commit()
        return {
            "success": True,
            "credits_deducted": payload.amount,
            "credits_remaining": remaining,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
