from pathlib import Path

from app.db.seed import seed
from app.db.sqlite import db, resolve_db_path
from app.logger import logger


def main() -> None:
    db_path = resolve_db_path()
    db.close()
    if db_path.exists():
        db_path.unlink()
    for suffix in ("-wal", "-shm"):
        extra = Path(f"{db_path}{suffix}")
        if extra.exists():
            extra.unlink()
    db.reopen()
    seed()
    logger.info("Database reset and seeded", {"dbPath": str(db_path)})


if __name__ == "__main__":
    main()
