from typing import NoReturn

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.auth.schemas import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest
from app.api.deps import get_current_user
from app.models.user import User
from app.security.jwt import bearer_scheme
from app.services.auth_client import auth_client

router = APIRouter()


def _raise_for_response(response: httpx.Response) -> NoReturn:
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    raise HTTPException(status_code=response.status_code, detail=detail)


@router.post("/register", status_code=201)
async def register(body: RegisterRequest) -> dict:
    try:
        return await auth_client.register(**body.model_dump(exclude_none=True))
    except httpx.HTTPStatusError as exc:
        _raise_for_response(exc.response)


@router.post("/login")
async def login(body: LoginRequest) -> dict:
    """Proxies the upstream response as-is - including a 403 consent_required,
    since only the auth service's own hosted /consent page can resolve it."""
    response = await auth_client.login(identifier=body.identifier, password=body.password)
    if response.status_code == 200:
        return response.json()
    _raise_for_response(response)


@router.post("/refresh")
async def refresh(body: RefreshRequest) -> dict:
    try:
        return await auth_client.refresh(refresh_token=body.refresh_token)
    except httpx.HTTPStatusError as exc:
        _raise_for_response(exc.response)


@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    try:
        await auth_client.logout(access_token=credentials.credentials, refresh_token=body.refresh_token)
    except httpx.HTTPStatusError as exc:
        _raise_for_response(exc.response)


@router.get("/me")
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Ensures a local user row exists (via get_current_user) and returns the
    live profile from the auth service - not cached locally, so it's always
    current and never duplicates identity data this app doesn't own."""
    try:
        return await auth_client.get_me(access_token=credentials.credentials)
    except httpx.HTTPStatusError as exc:
        _raise_for_response(exc.response)
