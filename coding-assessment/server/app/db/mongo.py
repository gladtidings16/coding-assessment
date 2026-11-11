import socket
from urllib.parse import urlparse, urlunparse

from pymongo import MongoClient
from pymongo.database import Database

from app.config import env
from app.logger import logger

# Basic driver connect. Task 2: make this safe across devices and networks.
mongo_ready = False
mongo_last_error: str | None = None
_client: MongoClient | None = None


def _ipv6_uri(uri: str) -> str:
    parsed = urlparse(uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 27017
    infos = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
    ipv6 = infos[0][4][0]
    auth = ""
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth += f":{parsed.password}"
        auth += "@"
    netloc = f"{auth}[{ipv6}]:{port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def connect_mongo() -> None:
    global mongo_ready, mongo_last_error, _client
    mongo_ready = False
    uri = _ipv6_uri(env.mongo_uri)
    client = MongoClient(
        uri,
        directConnection=env.mongo_uri.startswith("mongodb://"),
        serverSelectionTimeoutMS=2500,
        connectTimeoutMS=2000,
        socketTimeoutMS=2500,
        maxPoolSize=1,
        retryReads=False,
        retryWrites=False,
    )
    try:
        client.get_database().command("ping")
    except Exception:
        client.close()
        raise
    _client = client
    mongo_ready = True
    mongo_last_error = None
    logger.info("mongo driver connected")


def connect_mongo_safe() -> None:
    global mongo_ready, mongo_last_error
    try:
        connect_mongo()
    except Exception as err:
        mongo_ready = False
        mongo_last_error = str(err)
        logger.warn("mongo driver connect failed", {"error": mongo_last_error})


def get_mongo_db() -> Database | None:
    if _client is None or not mongo_ready:
        return None
    return _client[env.mongo_db_name]
