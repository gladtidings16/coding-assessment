import os
from pathlib import Path

from dotenv import load_dotenv

SERVER_DIR = Path(__file__).resolve().parents[1]
load_dotenv(SERVER_DIR / ".env")


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


class Env:
    node_env = os.environ.get("NODE_ENV", "development")
    port = _int("PORT", 4000)
    jwt_secret = os.environ.get("JWT_SECRET", "dev-secret")
    jwt_refresh_secret = os.environ.get("JWT_REFRESH_SECRET", "dev-refresh")
    jwt_expires_in = os.environ.get("JWT_EXPIRES_IN", "15m")
    jwt_refresh_expires_in = os.environ.get("JWT_REFRESH_EXPIRES_IN", "7d")
    database_path = os.environ.get("DATABASE_PATH", "./data/meridian.db")
    cors_origin = os.environ.get("CORS_ORIGIN", "http://localhost:5173")
    rate_limit_window_ms = _int("RATE_LIMIT_WINDOW_MS", 60_000)
    rate_limit_max = _int("RATE_LIMIT_MAX", 120)
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/meridian")
    mongo_db_name = os.environ.get("MONGODB_DB", "meridian")
    mongo_socket_host = os.environ.get("MONGODB_SOCKET_HOST", "127.0.0.1")
    mongo_socket_port = _int("MONGODB_SOCKET_PORT", 27017)


env = Env()
