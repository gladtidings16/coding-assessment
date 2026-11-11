import socketio

from app.config import env
from app.db import mongo, mongo_socket
from app.logger import logger

# Socket.IO starter. Task 2: tie this to Mongo-backed data and reconnect cleanly.
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[env.cors_origin],
    cors_credentials=True,
    ping_interval=5,
    ping_timeout=2,
)


@sio.event
async def connect(sid, environ):
    await sio.emit(
        "mongo:status",
        {"driver": mongo.mongo_ready, "tcp": mongo_socket.mongo_socket_state},
        to=sid,
    )


@sio.on("events:subscribe")
async def events_subscribe(sid):
    await sio.enter_room(sid, "events")


async def broadcast_event(payload: dict) -> None:
    await sio.emit("event:created", payload, room="events")


logger.info("socket.io attached")
