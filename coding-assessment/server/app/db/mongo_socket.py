import socket
import threading

from app.config import env
from app.logger import logger

# Raw TCP socket to Mongo. Task 2: replace this reconnect behavior.
mongo_socket_state = "down"
mongo_socket_last_error: str | None = None

_stop = threading.Event()
_thread: threading.Thread | None = None
_sock: socket.socket | None = None
_reconnect_attempts = 0


def _resolve_ipv6(host: str, port: int) -> tuple:
    infos = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
    return infos[0][4]


def _loop() -> None:
    global mongo_socket_state, mongo_socket_last_error, _sock, _reconnect_attempts
    while not _stop.is_set():
        mongo_socket_state = "reconnecting"
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        _sock = sock
        try:
            sock.settimeout(1.5)
            addr = _resolve_ipv6(env.mongo_socket_host, env.mongo_socket_port)
            sock.connect(addr)
            mongo_socket_state = "up"
            mongo_socket_last_error = None
            _reconnect_attempts = 0
            logger.info("mongo tcp socket connected")
            sock.settimeout(1.0)
            while not _stop.is_set():
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue
                if data == b"":
                    break
        except socket.timeout:
            mongo_socket_last_error = "socket timeout"
        except Exception as err:
            message = getattr(err, "strerror", None) or str(err)
            mongo_socket_last_error = message
        finally:
            try:
                sock.close()
            except OSError:
                pass
            if _sock is sock:
                _sock = None

        if _stop.is_set():
            break

        mongo_socket_state = "reconnecting"
        _reconnect_attempts += 1
        if _reconnect_attempts <= 3 or _reconnect_attempts % 10 == 0:
            logger.warn(
                "mongo tcp socket closed; reconnecting",
                {"error": mongo_socket_last_error, "attempt": _reconnect_attempts},
            )
        if _stop.wait(1.5):
            break


def start_mongo_socket() -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="mongo-tcp", daemon=True)
    _thread.start()


def stop_mongo_socket() -> None:
    _stop.set()
    sock = _sock
    if sock is not None:
        try:
            sock.close()
        except OSError:
            pass
