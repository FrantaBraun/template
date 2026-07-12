from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.account.schemas import AccountOut, AccountUpdate
from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=AccountOut)
async def get_account(current_user: User = Depends(get_current_user)) -> User:
    """Local account data only - never calls the auth service."""
    return current_user


@router.patch("/me", response_model=AccountOut)
async def update_account(
    body: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Local account data only - never calls the auth service."""
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user
