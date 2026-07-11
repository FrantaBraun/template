import uuid

import respx
from httpx import ASGITransport, AsyncClient, Response

from app.config import get_settings

AUTH_URL = get_settings().auth_url


@respx.mock
def test_register_proxies_upstream(client):
    respx.post(f"{AUTH_URL}/api/auth/register").mock(
        return_value=Response(201, json={"user": {"id": "u1"}, "verify_token": "tok"})
    )

    resp = client.post(
        "/api/auth/register",
        json={
            "email": "a@example.com",
            "login": "alogin",
            "password": "password123",
            "first_name": "A",
            "last_name": "B",
        },
    )

    assert resp.status_code == 201
    assert resp.json()["user"]["id"] == "u1"


@respx.mock
def test_login_success(client):
    respx.post(f"{AUTH_URL}/api/auth/login").mock(
        return_value=Response(
            200,
            json={
                "access_token": "a",
                "refresh_token": "r",
                "token_type": "bearer",
                "expires_in": 900,
            },
        )
    )

    resp = client.post("/api/auth/login", json={"identifier": "user", "password": "pw"})

    assert resp.status_code == 200
    assert resp.json()["access_token"] == "a"


@respx.mock
def test_login_consent_required_passthrough(client):
    respx.post(f"{AUTH_URL}/api/auth/login").mock(
        return_value=Response(
            403, json={"detail": {"consent_required": True, "application_group_id": "g1"}}
        )
    )

    resp = client.post("/api/auth/login", json={"identifier": "user", "password": "pw"})

    assert resp.status_code == 403
    assert resp.json()["detail"]["consent_required"] is True
    assert resp.json()["detail"]["application_group_id"] == "g1"


@respx.mock
def test_refresh_success(client):
    respx.post(f"{AUTH_URL}/api/auth/refresh").mock(
        return_value=Response(
            200,
            json={
                "access_token": "a2",
                "refresh_token": "r2",
                "token_type": "bearer",
                "expires_in": 900,
            },
        )
    )

    resp = client.post("/api/auth/refresh", json={"refresh_token": "old"})

    assert resp.status_code == 200
    assert resp.json()["access_token"] == "a2"


@respx.mock
def test_refresh_expired_propagates_401(client):
    respx.post(f"{AUTH_URL}/api/auth/refresh").mock(
        return_value=Response(401, json={"detail": "session expired"})
    )

    resp = client.post("/api/auth/refresh", json={"refresh_token": "bad"})

    assert resp.status_code == 401


@respx.mock
def test_logout_success(client):
    respx.post(f"{AUTH_URL}/api/auth/logout").mock(return_value=Response(204))

    resp = client.post(
        "/api/auth/logout",
        json={"refresh_token": "r"},
        headers={"Authorization": "Bearer sometoken"},
    )

    assert resp.status_code == 204


def test_logout_requires_bearer(client):
    resp = client.post("/api/auth/logout", json={"refresh_token": "r"})
    assert resp.status_code in (401, 403)


def test_me_requires_bearer(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


@respx.mock
async def test_me_creates_local_user_and_returns_upstream_profile(
    db_session, make_access_token, rsa_keypair, monkeypatch
):
    # TestClient drives the app from a separate thread with its own event
    # loop, which conflicts with db_session's connection (bound to this
    # test's loop). An in-process ASGI transport keeps everything on one loop.
    from app.database import get_db
    from app.main import app as fastapi_app

    _, public_pem = rsa_keypair
    monkeypatch.setattr("app.security.jwt._public_key", public_pem)
    sub = str(uuid.uuid4())
    token = make_access_token(sub=sub)

    respx.get(f"{AUTH_URL}/api/auth/me").mock(
        return_value=Response(200, json={"id": sub, "login": "alogin", "email": "a@example.com"})
    )

    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    try:
        transport = ASGITransport(app=fastapi_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 200
    assert resp.json()["login"] == "alogin"
