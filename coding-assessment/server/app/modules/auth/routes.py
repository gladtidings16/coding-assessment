import json
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response

from app.modules.auth.deps import require_auth
from app.modules.auth.service import (
    auth_service,
    parse_forgot,
    parse_login,
    parse_refresh,
    parse_register,
    parse_reset,
)

router = APIRouter()


async def read_json(request: Request) -> Any:
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return {}
    raw = await request.body()
    if len(raw) > 1_048_576:
        raise RuntimeError("payload too large")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise RuntimeError("invalid json") from err


@router.post("/login")
async def login(request: Request):
    email, password = parse_login(await read_json(request))
    return await auth_service.login(email, password)


@router.post("/refresh")
async def refresh(request: Request):
    token = parse_refresh(await read_json(request))
    return await auth_service.refresh(token)


@router.post("/logout")
async def logout(request: Request):
    body = await read_json(request)
    token = body.get("refreshToken") if isinstance(body, dict) else None
    await auth_service.logout(token)
    return Response(status_code=204)


@router.get("/me")
async def me(user: dict = Depends(require_auth)):
    return await auth_service.me(user["sub"])


@router.post("/register")
async def register(request: Request):
    body = parse_register(await read_json(request))
    user = await auth_service.register(body)
    return JSONResponse(status_code=201, content=user)


@router.post("/forgot-password")
async def forgot_password(request: Request):
    email = parse_forgot(await read_json(request))
    await auth_service.forgot_password(email)
    return {"ok": True}


@router.post("/reset-password")
async def reset_password(request: Request):
    token, password = parse_reset(await read_json(request))
    await auth_service.reset_password(token, password)
    return {"ok": True}
