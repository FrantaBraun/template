import time
import uuid

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import app.security.jwt as jwt_module
from app.config import Settings
from app.database import engine
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_public_key_cache():
    """app.security.jwt caches the auth service's public key in a module-level
    variable - reset it around every test so none of them leak state to another."""
    jwt_module._public_key = None
    yield
    jwt_module._public_key = None


def generate_rsa_keypair() -> tuple[str, str]:
    """Return (private_pem, public_pem) for a throwaway RSA keypair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


@pytest.fixture(scope="session")
def rsa_keypair() -> tuple[str, str]:
    return generate_rsa_keypair()


@pytest.fixture()
def make_access_token(rsa_keypair):
    """Factory fixture: make_access_token(sub=..., **claim_overrides) -> signed JWT string."""
    private_pem, _ = rsa_keypair

    def _make(sub: str | None = None, **overrides) -> str:
        now = int(time.time())
        claims = {
            "sub": sub or str(uuid.uuid4()),
            "email": "user@example.com",
            "login": "testuser",
            "role_name": "user",
            "email_verified": True,
            "subscription": None,
            "iat": now,
            "exp": now + 900,
        }
        claims.update(overrides)
        return pyjwt.encode(claims, private_pem, algorithm="RS256")

    return _make


@pytest.fixture()
async def db_session() -> AsyncSession:
    """A session bound to a rolled-back transaction, so tests never leave rows behind."""
    async with engine.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        async with session_factory() as session:
            yield session
        await connection.rollback()


@pytest.fixture()
def auth_test_settings() -> Settings:
    return Settings(auth_url="https://auth.test", auth_api_key="test-api-key")


@pytest.fixture()
def mail_test_settings() -> Settings:
    return Settings(
        mail_username="test-user",
        mail_password="test-pass",
        mail_from="noreply@example.com",
        mail_server="smtp.example.com",
        mail_port=587,
        mail_starttls=True,
        mail_ssl_tls=False,
        mail_suppress_send=True,
    )
