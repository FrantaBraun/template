from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.security.jwt import get_current_user_claims


async def get_current_user(
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the local User row for a verified JWT's sub claim, creating it
    on first sight. Uses INSERT ... ON CONFLICT DO NOTHING rather than a naive
    check-then-insert, since two near-simultaneous first requests from the
    same brand-new user (e.g. /me firing right after /login) can otherwise
    race the auth_sub uniqueness constraint."""
    auth_sub = UUID(claims["sub"])

    result = await db.execute(select(User).where(User.auth_sub == auth_sub))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    await db.execute(
        pg_insert(User).values(auth_sub=auth_sub).on_conflict_do_nothing(index_elements=[User.auth_sub])
    )
    await db.commit()

    result = await db.execute(select(User).where(User.auth_sub == auth_sub))
    return result.scalar_one()
