import uuid

from httpx import ASGITransport, AsyncClient


async def _account_request(db_session, make_access_token, method: str, sub: str | None = None, **kwargs):
    # Same rationale as test_auth_router.py's _me_request: TestClient runs the
    # app in a separate thread with its own event loop, which conflicts with
    # db_session's connection. ASGITransport keeps everything on one loop.
    from app.database import get_db
    from app.main import app as fastapi_app

    sub = sub or str(uuid.uuid4())
    token = make_access_token(sub=sub)

    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    try:
        transport = ASGITransport(app=fastapi_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            return await ac.request(
                method, "/api/account/me", headers={"Authorization": f"Bearer {token}"}, **kwargs
            )
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)


async def test_get_account_creates_and_returns_row(db_session, make_access_token, rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr("app.security.jwt._public_key", public_pem)
    sub = str(uuid.uuid4())

    resp = await _account_request(db_session, make_access_token, "GET", sub=sub)

    assert resp.status_code == 200
    assert resp.json()["nickname"] is None


async def test_patch_account_updates_nickname(db_session, make_access_token, rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair
    monkeypatch.setattr("app.security.jwt._public_key", public_pem)
    sub = str(uuid.uuid4())

    resp = await _account_request(
        db_session, make_access_token, "PATCH", sub=sub, json={"nickname": "Frantisek"}
    )

    assert resp.status_code == 200
    assert resp.json()["nickname"] == "Frantisek"


async def test_account_me_requires_bearer_token(client):
    resp = client.get("/api/account/me")
    assert resp.status_code in (401, 403)
