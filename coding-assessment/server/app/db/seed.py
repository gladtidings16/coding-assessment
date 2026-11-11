import uuid

import bcrypt

from app.db.sqlite import db, migrate
from app.logger import now_iso


def seed() -> None:
    migrate()
    row = db.query_one("SELECT COUNT(*) as c FROM users")
    if row is not None and row["c"] > 0:
        return

    ts = now_iso()
    password_hash = bcrypt.hashpw(b"Admin123!", bcrypt.gensalt(rounds=10)).decode()
    db.execute(
        """INSERT INTO users (id, email, password_hash, name, role, is_active, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
        (str(uuid.uuid4()), "admin@meridian.test", password_hash, "Amina Okonkwo", "admin", ts, ts),
    )
