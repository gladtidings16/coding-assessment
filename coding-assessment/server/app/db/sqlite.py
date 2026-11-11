import sqlite3
import threading
from pathlib import Path

from app.config import SERVER_DIR, env

_lock = threading.Lock()


def resolve_db_path() -> Path:
    raw = Path(env.database_path)
    path = raw if raw.is_absolute() else (SERVER_DIR / raw).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class Db:
    def __init__(self) -> None:
        self.conn = self._open()

    def _open(self) -> sqlite3.Connection:
        conn = sqlite3.connect(resolve_db_path(), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def query_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with _lock:
            return self.conn.execute(sql, params).fetchone()

    def execute(self, sql: str, params: tuple = ()) -> None:
        with _lock:
            self.conn.execute(sql, params)
            self.conn.commit()

    def exec_script(self, sql: str) -> None:
        with _lock:
            self.conn.executescript(sql)
            self.conn.commit()

    def close(self) -> None:
        with _lock:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass

    def reopen(self) -> None:
        with _lock:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
            self.conn = self._open()


db = Db()


def migrate() -> None:
    sql = (Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8")
    db.exec_script(sql)
