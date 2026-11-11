import socketio

from app.main import app as fastapi_app
from app.realtime.socket import sio

application = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
