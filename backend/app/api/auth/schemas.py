from pydantic import BaseModel, EmailStr


class EmailParams(BaseModel):
    """Matches auth.withfbraun.com's EmailTemplateParams - any field left
    unset uses the service's default (English) text."""

    title: str | None = None
    greeting: str | None = None
    message: str | None = None
    expire_units: str | None = None
    button_text: str | None = None
    instructions: str | None = None
    footer_text: str | None = None


class RegisterRequest(BaseModel):
    email: EmailStr
    login: str
    password: str
    first_name: str
    last_name: str
    language_code: str | None = None
    verify_url: str | None = None
    send_verify_email: bool = True
    email_params: EmailParams | None = None


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
