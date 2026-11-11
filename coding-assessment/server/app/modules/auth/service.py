import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import env
from app.db.sqlite import db
from app.errors import bad_request, not_implemented, unauthorized
from app.logger import now_iso

_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def expires_seconds(value: str) -> int:
    text = value.strip()
    if text and text[-1] in _UNITS and text[:-1].isdigit():
        return int(text[:-1]) * _UNITS[text[-1]]
    return int(text)


def _sign_access(user) -> str:
    now = int(time.time())
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + expires_seconds(env.jwt_expires_in),
    }
    return jwt.encode(payload, env.jwt_secret, algorithm="HS256")


def _sign_refresh(user_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "typ": "refresh",
        "iat": now,
        "exp": now + expires_seconds(env.jwt_refresh_expires_in),
    }
    return jwt.encode(payload, env.jwt_refresh_secret, algorithm="HS256")


def _public(user) -> dict[str, str]:
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}


def _validation(field_errors: dict[str, list[str]]) -> None:
    bad_request("Validation failed", {"formErrors": [], "fieldErrors": field_errors})


def parse_login(body: Any) -> tuple[str, str]:
    if not isinstance(body, dict):
        _validation({})
    errors: dict[str, list[str]] = {}
    email = body.get("email")
    password = body.get("password")
    if "email" not in body:
        errors["email"] = ["Required"]
    elif not isinstance(email, str) or not _EMAIL.match(email):
        errors["email"] = ["Invalid email"]
    if "password" not in body:
        errors["password"] = ["Required"]
    elif not isinstance(password, str) or len(password) < 1:
        errors["password"] = ["String must contain at least 1 character(s)"]
    if errors:
        _validation(errors)
    return email, password


def parse_refresh(body: Any) -> str:
    if not isinstance(body, dict):
        _validation({})
    token = body.get("refreshToken")
    if "refreshToken" not in body:
        _validation({"refreshToken": ["Required"]})
    if not isinstance(token, str) or len(token) < 1:
        _validation({"refreshToken": ["String must contain at least 1 character(s)"]})
    return token


def parse_register(body: Any) -> dict:
    if not isinstance(body, dict):
        _validation({})
    errors: dict[str, list[str]] = {}
    email = body.get("email")
    password = body.get("password")
    name = body.get("name")
    if "email" not in body:
        errors["email"] = ["Required"]
    elif not isinstance(email, str) or not _EMAIL.match(email):
        errors["email"] = ["Invalid email"]
    if "password" not in body:
        errors["password"] = ["Required"]
    elif not isinstance(password, str) or len(password) < 8:
        errors["password"] = ["String must contain at least 8 character(s)"]
    if "name" not in body:
        errors["name"] = ["Required"]
    elif not isinstance(name, str) or len(name) < 1:
        errors["name"] = ["String must contain at least 1 character(s)"]
    if errors:
        _validation(errors)
    return body


def parse_forgot(body: Any) -> str:
    if not isinstance(body, dict):
        _validation({})
    email = body.get("email")
    if "email" not in body:
        _validation({"email": ["Required"]})
    if not isinstance(email, str) or not _EMAIL.match(email):
        _validation({"email": ["Invalid email"]})
    return email


def parse_reset(body: Any) -> tuple[str, str]:
    if not isinstance(body, dict):
        _validation({})
    errors: dict[str, list[str]] = {}
    token = body.get("token")
    password = body.get("password")
    if "token" not in body or not isinstance(token, str):
        errors["token"] = ["Required"]
    if "password" not in body:
        errors["password"] = ["Required"]
    elif not isinstance(password, str) or len(password) < 8:
        errors["password"] = ["String must contain at least 8 character(s)"]
    if errors:
        _validation(errors)
    return token, password


# Conventional credential login. Task 1 may extend states, sessions, and UX around this.
class AuthService:
    async def login(self, email: str, password: str) -> dict:
        user = db.query_one("SELECT * FROM users WHERE email = ?", (email,))
        if user is None or not user["is_active"]:
            unauthorized("Invalid credentials")
        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            unauthorized("Invalid credentials")

        access_token = _sign_access(user)
        refresh_token = _sign_refresh(user["id"])
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat().replace("+00:00", "Z")
        db.execute(
            """INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, revoked_at, created_at)
               VALUES (?, ?, ?, ?, NULL, ?)""",
            (str(uuid.uuid4()), user["id"], refresh_token, expires_at, now_iso()),
        )
        return {
            "user": _public(user),
            "tokens": {
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "expiresIn": env.jwt_expires_in,
            },
        }

    async def refresh(self, _refresh_token: str) -> dict:
        not_implemented("authService.refresh")

    async def logout(self, _refresh_token: str | None) -> None:
        return None

    async def me(self, user_id: str) -> dict:
        user = db.query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if user is None:
            unauthorized()
        return _public(user)

    async def register(self, _body: Any) -> dict:
        not_implemented("authService.register")

    async def forgot_password(self, _email: str) -> None:
        not_implemented("authService.forgotPassword")

    async def reset_password(self, _token: str, _password: str) -> None:
        not_implemented("authService.resetPassword")


auth_service = AuthService()
