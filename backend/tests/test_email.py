# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

"""Tests for app.services.email.send_email, using MAIL_SUPPRESS_SEND so no
real SMTP connection is opened while still asserting on the built message."""

from fastapi_mail import FastMail

from app.services.email import _connection_config, send_email


async def test_send_email_suppressed_does_not_raise(mail_test_settings):
    await send_email(
        subject="Hello",
        recipients=["someone@example.com"],
        body="Test body",
        settings=mail_test_settings,
    )


async def test_send_email_builds_expected_message(mail_test_settings):
    mail = FastMail(_connection_config(mail_test_settings))

    with mail.record_messages() as outbox:
        await send_email(
            subject="Hello",
            recipients=["someone@example.com"],
            body="Test body",
            settings=mail_test_settings,
        )

    assert len(outbox) == 1
    sent = outbox[0]
    assert sent["Subject"] == "Hello"
    assert "someone@example.com" in sent["To"]


async def test_send_email_allows_per_call_overrides(mail_test_settings):
    mail = FastMail(_connection_config(mail_test_settings))

    with mail.record_messages() as outbox:
        await send_email(
            subject="Hello",
            recipients=["someone@example.com"],
            body="Test body",
            settings=mail_test_settings,
            MAIL_FROM="override@example.com",
        )

    assert "override@example.com" in outbox[0]["From"]
