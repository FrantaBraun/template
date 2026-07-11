import asyncio

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_client import AuthClient, auth_client

bearer_scheme = HTTPBearer()

_public_key: str | None = None
_public_key_lock = asyncio.Lock()


async def get_public_key(client: AuthClient | None = None) -> str:
    """Fetch the auth service's RS256 public key once and cache it in-process.

    Deliberately not functools.lru_cache: that caches the coroutine object of
    an async def, not its awaited result, so a second call would try to
    re-await an already-consumed coroutine. A plain module-level variable
    guarded by a lock is the correct async equivalent of "fetch once, cache
    forever".
    """
    global _public_key
    if _public_key is None:
        async with _public_key_lock:
            if _public_key is None:
                _public_key = await (client or auth_client).get_public_key()
    return _public_key


async def get_current_user_claims(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Verify the bearer token locally against the cached public key - no
    round-trip to the auth service on every request."""
    public_key = await get_public_key()
    try:
        return jwt.decode(credentials.credentials, public_key, algorithms=["RS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
