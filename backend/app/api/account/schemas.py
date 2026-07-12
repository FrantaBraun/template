import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountOut(BaseModel):
    """The local account record - data this app owns outright, distinct from
    the auth service's identity data returned by /api/auth/me."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nickname: str | None
    created_at: datetime
    updated_at: datetime


class AccountUpdate(BaseModel):
    nickname: str | None = None
