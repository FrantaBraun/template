from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    login: str
    password: str
    first_name: str
    last_name: str
    language_code: str | None = None
    verify_url: str | None = None
    send_verify_email: bool = True
    email_params: dict | None = None


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
