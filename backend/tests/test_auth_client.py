import httpx
import pytest
import respx
from httpx import Response

from app.config import Settings
from app.services.auth_client import AuthClient


@respx.mock
async def test_register_success(auth_test_settings):
    respx.post("https://auth.test/api/auth/register").mock(
        return_value=Response(201, json={"user": {"id": "u1"}, "verify_token": "tok"})
    )
    client = AuthClient(auth_test_settings)
    result = await client.register(
        email="a@example.com", login="alogin", password="password123", first_name="A", last_name="B"
    )
    assert result["user"]["id"] == "u1"
    await client.aclose()


@respx.mock
async def test_register_sends_api_key_header(auth_test_settings):
    route = respx.post("https://auth.test/api/auth/register").mock(
        return_value=Response(201, json={"user": {}, "verify_token": "tok"})
    )
    client = AuthClient(auth_test_settings)
    await client.register(
        email="a@example.com", login="alogin", password="password123", first_name="A", last_name="B"
    )
    assert route.calls.last.request.headers["X-Api-Key"] == "test-api-key"
    await client.aclose()


@respx.mock
async def test_login_success_returns_response(auth_test_settings):
    respx.post("https://auth.test/api/auth/login").mock(
        return_value=Response(
            200, json={"access_token": "a", "refresh_token": "r", "token_type": "bearer"}
        )
    )
    client = AuthClient(auth_test_settings)
    resp = await client.login(identifier="user", password="pw")
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "a"
    await client.aclose()


@respx.mock
async def test_login_consent_required_does_not_raise(auth_test_settings):
    respx.post("https://auth.test/api/auth/login").mock(
        return_value=Response(
            403, json={"detail": {"consent_required": True, "application_group_id": "g1"}}
        )
    )
    client = AuthClient(auth_test_settings)
    resp = await client.login(identifier="user", password="pw")
    assert resp.status_code == 403
    assert resp.json()["detail"]["consent_required"] is True
    await client.aclose()


@respx.mock
async def test_refresh_raises_on_401(auth_test_settings):
    respx.post("https://auth.test/api/auth/refresh").mock(return_value=Response(401, json={}))
    client = AuthClient(auth_test_settings)
    with pytest.raises(httpx.HTTPStatusError):
        await client.refresh(refresh_token="bad")
    await client.aclose()


@respx.mock
async def test_logout_success(auth_test_settings):
    respx.post("https://auth.test/api/auth/logout").mock(return_value=Response(204))
    client = AuthClient(auth_test_settings)
    await client.logout(access_token="a", refresh_token="r")
    await client.aclose()


@respx.mock
async def test_get_me(auth_test_settings):
    respx.get("https://auth.test/api/auth/me").mock(
        return_value=Response(200, json={"id": "u1", "login": "alogin"})
    )
    client = AuthClient(auth_test_settings)
    me = await client.get_me(access_token="a")
    assert me["login"] == "alogin"
    await client.aclose()


@respx.mock
async def test_get_public_key(auth_test_settings):
    respx.get("https://auth.test/api/auth/public-key").mock(
        return_value=Response(200, json={"public_key": "PEMDATA", "algorithm": "RS256"})
    )
    client = AuthClient(auth_test_settings)
    key = await client.get_public_key()
    assert key == "PEMDATA"
    await client.aclose()


@respx.mock
async def test_register_without_api_key_raises_before_any_request():
    """An empty X-Api-Key isn't rejected by the auth service - it's silently
    treated as no application context, skipping the consent check entirely.
    register()/login() must fail loudly instead of sending it anyway."""
    route = respx.post("https://auth.test/api/auth/register").mock(return_value=Response(201))
    client = AuthClient(Settings(auth_url="https://auth.test", auth_api_key=""))

    with pytest.raises(RuntimeError):
        await client.register(
            email="a@example.com", login="alogin", password="password123", first_name="A", last_name="B"
        )

    assert route.call_count == 0
    await client.aclose()


@respx.mock
async def test_login_without_api_key_raises_before_any_request():
    route = respx.post("https://auth.test/api/auth/login").mock(return_value=Response(200))
    client = AuthClient(Settings(auth_url="https://auth.test", auth_api_key=""))

    with pytest.raises(RuntimeError):
        await client.login(identifier="user", password="pw")

    assert route.call_count == 0
    await client.aclose()
