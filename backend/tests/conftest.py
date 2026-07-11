import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


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
