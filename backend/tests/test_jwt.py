# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

"""Tests for app.security.jwt: public-key fetch/caching and local RS256
verification of access tokens (valid, expired, wrong-key, malformed)."""

import time

import pytest
import respx
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from httpx import Response

import app.security.jwt as jwt_module
from app.security.jwt import get_current_user_claims, get_public_key
from app.services.auth_client import AuthClient
from tests.conftest import generate_rsa_keypair


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@respx.mock
async def test_get_public_key_fetches_and_caches(rsa_keypair, auth_test_settings):
    _, public_pem = rsa_keypair
    route = respx.get("https://auth.test/api/auth/public-key").mock(
        return_value=Response(200, json={"public_key": public_pem, "algorithm": "RS256"})
    )
    client = AuthClient(auth_test_settings)

    key1 = await get_public_key(client=client)
    key2 = await get_public_key(client=client)

    assert key1 == public_pem == key2
    assert route.call_count == 1
    await client.aclose()


async def test_valid_token_returns_claims(make_access_token, rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr(jwt_module, "_public_key", public_pem)
    token = make_access_token(sub="11111111-1111-1111-1111-111111111111", role_name="integrator")

    claims = await get_current_user_claims(_credentials(token))

    assert claims["sub"] == "11111111-1111-1111-1111-111111111111"
    assert claims["role_name"] == "integrator"


async def test_expired_token_raises_401(make_access_token, rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr(jwt_module, "_public_key", public_pem)
    token = make_access_token(exp=int(time.time()) - 10)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_claims(_credentials(token))

    assert exc_info.value.status_code == 401


async def test_token_signed_with_wrong_key_raises_401(make_access_token, rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr(jwt_module, "_public_key", public_pem)
    other_private_pem, _ = generate_rsa_keypair()

    import jwt as pyjwt

    forged = pyjwt.encode(
        {"sub": "attacker", "exp": int(time.time()) + 900}, other_private_pem, algorithm="RS256"
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_claims(_credentials(forged))

    assert exc_info.value.status_code == 401


async def test_malformed_token_raises_401(rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr(jwt_module, "_public_key", public_pem)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_claims(_credentials("not-a-jwt"))

    assert exc_info.value.status_code == 401
