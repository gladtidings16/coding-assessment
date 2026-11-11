import sys

import uvicorn

from app.config import env


def main() -> None:
    reload = "--no-reload" not in sys.argv
    uvicorn.run(
        "app.asgi:application",
        host="0.0.0.0",
        port=env.port,
        reload=reload,
        reload_dirs=["app"] if reload else None,
    )


if __name__ == "__main__":
    main()
