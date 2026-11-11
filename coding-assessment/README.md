# Coding Assessment — Starter Kit

Read **[task.md](./task.md)** first. You have **15 minutes**. Choose **one** task.

This repository is a **starting structure**. Login works. MongoDB, REST events, and sockets are wired as basic stubs so you can implement your chosen task without rebuilding the project from scratch.

The API is a Python FastAPI server. It keeps the same HTTP routes, JWT login, SQLite users, Mongo events, and Socket.IO events the frontend already uses.

## Run

Requires Node.js 22+ for the frontend and Python 3.11+ for the API.

```bash
python3 -m venv server/.venv
server/.venv/bin/pip install -r server/requirements.txt
npm install
npm run db:reset
npm run dev
```

- Web: http://localhost:5173
- API: http://localhost:4000
- Health: `GET http://localhost:4000/api/health`

Seed login: `admin@meridian.test` / `Admin123!`

## Where to work

| Task | Start here |
| --- | --- |
| **1 — Authentication workflow** | `frontend/src/features/auth/` · `frontend/src/context/AuthContext.tsx` · `server/app/modules/auth/` |
| **2 — MongoDB + REST + sockets** | `server/app/db/mongo.py` · `server/app/db/mongo_socket.py` · `server/app/realtime/` · `server/app/modules/events/` · `frontend/src/features/live/` |

SQLite holds seed users so the HTTP API boots even when Mongo is down.
