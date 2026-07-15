# Backend (FastAPI)

Run locally:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API health: `http://localhost:8000/health`

Initialize database tables (development only):

```bash
# with env vars set (or .env configured)
curl -X POST http://localhost:8000/dev/init-db
```
Alembic migrations (recommended)

Initialize and run migrations:

```bash
cd backend
# initialize alembic (already scaffolded in repo)
# generate an initial migration (autogenerate requires DB metadata and DB access)
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Note: The `/dev/init-db` route exists for quick local setups but is gated by the `ALLOW_DEV_INIT` env flag. Prefer Alembic for reproducible migrations.

