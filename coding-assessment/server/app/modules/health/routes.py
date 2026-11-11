from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db import mongo
from app.db import mongo_socket as mongo_tcp
from app.db.sqlite import db
from app.logger import now_iso

router = APIRouter()


def health():
    return {
        "status": "ok",
        "service": "meridian-api",
        "ts": now_iso(),
        "mongo": {
            "driver": "up" if mongo.mongo_ready else "down",
            "driverError": mongo.mongo_last_error,
            "socket": mongo_tcp.mongo_socket_state,
            "socketError": mongo_tcp.mongo_socket_last_error,
        },
    }


def ready():
    try:
        db.query_one("SELECT 1")
    except Exception:
        return JSONResponse(status_code=503, content={"ready": False})
    return {"ready": True, "mongo": mongo.mongo_ready}


router.add_api_route("", health, methods=["GET"])
router.add_api_route("/", health, methods=["GET"])
router.add_api_route("/ready", ready, methods=["GET"])
