import jwt
from fastapi import Request

from app.config import env
from app.errors import unauthorized


def require_auth(request: Request) -> dict:
    header = request.headers.get("authorization")
    if not header or not header.startswith("Bearer "):
        unauthorized("Missing bearer token")
    token = header[len("Bearer ") :]
    try:
        payload = jwt.decode(token, env.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        unauthorized("Invalid or expired token")
    return payload
