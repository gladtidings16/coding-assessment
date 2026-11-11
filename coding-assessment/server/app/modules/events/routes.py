import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.db import mongo
from app.db.mongo import get_mongo_db
from app.logger import now_iso
from app.modules.auth.deps import require_auth
from app.realtime.socket import broadcast_event

# REST surface over a Mongo `events` collection.
# Task 2: connection, writes, reads, and socket fan-out all start here.
router = APIRouter()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def serialize_event(doc: dict) -> dict:
    out = {}
    for key, value in doc.items():
        if key == "_id":
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = _iso(value)
        else:
            out[key] = value
    return out


def _list_events(database) -> list[dict]:
    cursor = database["events"].find({}).sort("createdAt", -1).limit(50)
    return [serialize_event(doc) for doc in cursor]


async def list_events(_user: dict = Depends(require_auth)):
    database = get_mongo_db()
    if database is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "MONGO_UNAVAILABLE",
                    "message": mongo.mongo_last_error or "Mongo is not connected",
                },
                "mongo": mongo.mongo_ready,
            },
        )
    data = await asyncio.to_thread(_list_events, database)
    return {"data": data}


async def create_event(request: Request, user: dict = Depends(require_auth)):
    database = get_mongo_db()
    if database is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "MONGO_UNAVAILABLE",
                    "message": mongo.mongo_last_error or "Mongo is not connected",
                },
            },
        )
    body = {}
    raw = await request.body()
    if raw:
        import json

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as err:
            raise RuntimeError("invalid json") from err
        if isinstance(parsed, dict):
            body = parsed
    text = body.get("body")
    if text is None:
        text = ""
    else:
        text = str(text)
    doc = {
        "_id": str(uuid.uuid4()),
        "body": text.strip() or "untitled",
        "authorId": user["sub"],
        "createdAt": now_iso(),
    }
    await asyncio.to_thread(database["events"].insert_one, doc)
    await broadcast_event(doc)
    return JSONResponse(status_code=201, content=doc)


router.add_api_route("", list_events, methods=["GET"])
router.add_api_route("/", list_events, methods=["GET"])
router.add_api_route("", create_event, methods=["POST"])
router.add_api_route("/", create_event, methods=["POST"])
