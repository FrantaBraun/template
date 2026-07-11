import httpx

from app.config import Settings, get_settings


class AuthClient:
    """Async client for auth.withfbraun.com, the shared authorization service.

    Every method except `login` raises via response.raise_for_status() on a
    non-2xx response. `login` is the one call that must NOT raise on 403:
    the caller needs to distinguish "200 with tokens" from "403
    consent_required" itself, and raising would collapse that distinction.
    """

    def __init__(self, settings: Settings | None = None):
        settings = settings or get_settings()
        self._http = httpx.AsyncClient(
            base_url=settings.auth_url,
            headers={"X-Api-Key": settings.auth_api_key},
            timeout=15,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def register(
        self,
        *,
        email: str,
        login: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra: object,
    ) -> dict:
        r = await self._http.post(
            "/api/auth/register",
            json={
                "email": email,
                "login": login,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                **extra,
            },
        )
        r.raise_for_status()
        return r.json()

    async def login(self, *, identifier: str, password: str) -> httpx.Response:
        """Returns the raw response - inspect .status_code: 200 = tokens in
        body, 403 = consent_required, anything else = a real error."""
        return await self._http.post(
            "/api/auth/login", json={"identifier": identifier, "password": password}
        )

    async def refresh(self, *, refresh_token: str) -> dict:
        r = await self._http.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        r.raise_for_status()
        return r.json()

    async def logout(self, *, access_token: str, refresh_token: str) -> None:
        r = await self._http.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()

    async def get_me(self, *, access_token: str) -> dict:
        r = await self._http.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        r.raise_for_status()
        return r.json()

    async def get_public_key(self) -> str:
        r = await self._http.get("/api/auth/public-key")
        r.raise_for_status()
        return r.json()["public_key"]

    async def get_consent_info(self, *, group_id: str, access_token: str) -> dict:
        r = await self._http.get(
            f"/api/auth/consent-info/{group_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json()

    async def grant_consent(self, *, group_id: str, access_token: str) -> None:
        r = await self._http.post(
            f"/api/auth/consent/{group_id}/grant",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()

    async def reject_consent(self, *, group_id: str, access_token: str) -> None:
        r = await self._http.post(
            f"/api/auth/consent/{group_id}/reject",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()


auth_client = AuthClient()
