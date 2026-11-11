import json
import sys
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _emit(level: str, msg: str, extra: Any = None) -> None:
    payload: dict[str, Any] = {"level": level, "msg": msg}
    if extra is not None:
        payload["extra"] = extra
    payload["ts"] = now_iso()
    line = json.dumps(payload)
    if level == "info":
        print(line, flush=True)
    else:
        print(line, file=sys.stderr, flush=True)


class Logger:
    def info(self, msg: str, extra: Any = None) -> None:
        _emit("info", msg, extra)

    def warn(self, msg: str, extra: Any = None) -> None:
        _emit("warn", msg, extra)

    def error(self, msg: str, extra: Any = None) -> None:
        _emit("error", msg, extra)


logger = Logger()
