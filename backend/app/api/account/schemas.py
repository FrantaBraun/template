# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

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
    """PATCH /api/account/me body - all fields optional, applied via
    exclude_unset so omitted fields are left untouched rather than cleared."""

    nickname: str | None = None
