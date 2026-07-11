# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a template repository for bootstrapping new full-stack applications. It has three independently versioned and deployed components: `backend/` (FastAPI), `frontend/` (Vite/React), and `scripts/` (build + deployment tooling). They don't share a release cadence — see "Independent versioning" below.

## Workflow requirements

- **Commit after every change.** Once a change (feature, fix, config edit) is complete and working, create a git commit for it before moving on to the next one.
- **Every backend change needs test coverage.** After adding or modifying anything under `backend/app/`, create or update the matching test(s) under `backend/tests/` in the same change — do not leave backend code changes untested.

## Commands

### Backend (`backend/`)
Runs from a local venv at `backend/.venv` (Python 3.14). All commands below assume cwd = `backend/`.
- Dev server: `.venv/Scripts/python.exe -m uvicorn app.main:app --reload` (port 8000)
- All tests: `.venv/Scripts/python.exe -m pytest`
- Single file: `.venv/Scripts/python.exe -m pytest tests/test_email.py`
- Single test: `.venv/Scripts/python.exe -m pytest tests/test_email.py::test_send_email_suppressed_does_not_raise`
- New migration: `.venv/Scripts/python.exe -m alembic revision --autogenerate -m "message"`
- Apply migrations: `.venv/Scripts/python.exe -m alembic upgrade head`
- After adding a dependency: install it, then re-freeze with `pip freeze > requirements.txt` (the file is a full freeze of the venv, not a hand-maintained list)

### Frontend (`frontend/`)
- Dev server: `npm run dev` (port 5173)
- Build (typecheck + bundle): `npm run build` — runs `tsc` (noEmit type-check) then `vite build`
- Preview production build: `npm run preview`

## Architecture

### Backend: config, routing, DB, logging, email
- All settings load through `app/config.py`'s `Settings` (pydantic-settings), sourced from `backend/.env` (see `.env.example`). `BASE_DIR` there anchors all relative paths (env file, log dir) to `backend/` regardless of the process's cwd.
- All REST routes are mounted under the `/api` prefix via `app/api/router.py`, which aggregates sub-routers (e.g. `app/api/public/version.py`). Add new endpoints as their own `APIRouter` and wire them into `api_router` there, rather than adding routes directly in `main.py`.
- DB access is async-only: SQLAlchemy's async engine + `asyncpg` (the `DATABASE_URL` scheme is `postgresql+asyncpg://`, which has no sync counterpart — don't reach for `psycopg2`-style sync sessions). `app/models/base.py` has an empty `Base`; no concrete models exist yet in this template.
- Alembic is wired for the async engine (`alembic init -t async`). `alembic/env.py` pulls the connection string from `Settings.database_url`, not from the static placeholder in `alembic.ini`, and sets `prepend_sys_path = %(here)s` so `import app` resolves regardless of invocation directory.
- Logging is configured once at import time in `main.py` via `configure_logging()` (`app/logging_config.py`) — a `TimedRotatingFileHandler` + console handler attached to the root logger. **Naming mismatch to resolve before relying on this:** `app/config.py` reads `LOG_LEVEL` / `LOG_DIR` / `LOG_ROTATION_WHEN` / `LOG_ROTATION_INTERVAL` / `LOG_ROTATION_BACKUP_COUNT`, but `.env.example` currently defines differently-named keys (`LOGGING_DIR`, `LOGGING_FILENAME`, `LOGGING_DAYS_HISTORY`, `LOGGING_MESSAGE_FORMAT`, `LOGGING_LEVEL`). Since `Settings` silently ignores unknown env keys, none of the `LOGGING_*` values currently take effect — log filename and message format can't be customized today. Reconcile the naming in one direction before depending on it.
- Email goes through `app/services/email.py`'s `send_email()`, built on `fastapi-mail`. Connection defaults come from `Settings` (`MAIL_*` in `.env`), but every `ConnectionConfig` field can be overridden per call via kwargs (e.g. a one-off `MAIL_FROM`). `MAIL_SUPPRESS_SEND=true` still builds and dispatches the message internally (so tests can assert on it via `FastMail(...).record_messages()`), it just skips opening a real SMTP connection.

### Cross-cutting: backend and frontend version independently
- `backend/version.json` and `frontend/public/version.json` are separate, independently-maintained version markers — there is no shared version number between the two components.
- `GET /api/public/version` reads and returns `backend/version.json` verbatim.
- The frontend's `/version` page (`frontend/src/pages/Version.tsx`) fetches both that endpoint and its own `/version.json`, and flags a mismatch whenever their major.minor versions differ.
- `scripts/build.py` packages and tags backend/frontend releases separately (git tags `B-x.y.z` / `F-x.y.z`), so the two genuinely drift independently in normal operation — the `/version` page's compatibility check is the runtime signal for when that drift matters.

### Frontend: routing, auth client, styling
- Routes are declared in `App.tsx` (react-router-dom) and wrapped by `AuthProvider` + `BrowserRouter` in `main.tsx`; page-level chrome comes from `components/Layout.tsx`.
- `api/client.ts` owns the API base URL (`VITE_API_URL`) and the JWT access/refresh token lifecycle: `apiFetch()` attaches the bearer token and transparently retries once via `/api/auth/refresh` on a 401. **`AuthContext` and `client.ts` already call `/api/auth/me`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh` — none of these exist in this template's backend yet** (only `/api/public/version` is implemented server-side so far). Implementing real auth means matching the API surface the frontend client already expects, not designing a new contract from scratch.
- Tailwind is v4, CSS-first: there is no `tailwind.config.js`. `src/index.css` just does `@import "tailwindcss"` plus a handful of hand-written base styles, and the `@tailwindcss/vite` plugin (in `vite.config.ts`) handles content detection automatically.
- `CORS_ORIGINS` in `backend/.env.example` defaults to `["http://localhost:3000"]`, but the frontend dev server defaults to port 5173 (`VITE_APP_URL` in `frontend/.env.example`) — a fresh checkout following both `.env.example` files as-is will hit CORS errors between the two dev servers until one side is adjusted.

### Deployment (`scripts/`)
- `build.py` archives `backend/` / `frontend/` / `scripts/` from a git ref (a `B-`/`F-` tag in STABLE mode, `HEAD` in SNAPSHOT mode), builds the frontend with `npm install && npm run build`, and uploads the resulting zip to FTP per `scripts/build.config.toml` (gitignored; copy from `.example`).
- `install.sh` / `upgrade.sh` are Linux-only systemd + nginx deployment scripts (require `psql`, `nginx`, `systemctl` on `PATH`) driven by `scripts/deploy.config.sh` (gitignored; copy from `.example`). They provision the Postgres role/DB from `backend/.env`'s `DATABASE_URL`, and health-check via `GET /api/public/version` after `upgrade.sh` restarts the service — a change that breaks that endpoint will trigger `upgrade.sh`'s automatic rollback.
