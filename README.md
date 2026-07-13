# Fitness Diary

Fitness Diary is a minimal fullstack diary app with a split backend.

## Architecture

- Frontend: HTML, CSS, JavaScript
- Auth service: FastAPI, JWT, password hashing
- Diary service: FastAPI, protected diary entries
- Database: Supabase PostgreSQL
- ORM: SQLAlchemy

## Services

- `backend/auth-service` handles registration, login, JWT issuing, and `/me`.
- `backend/diary-service` handles creating and reading diary entries.
- `frontend` is the local frontend source.
- `docs` is the GitHub Pages copy of the frontend.

## Local Run

Auth service:

```bash
cd backend/auth-service
venv/bin/python -m uvicorn app.main:app --port 8100
```

Diary service:

```bash
cd backend/diary-service
venv/bin/python -m uvicorn app.main:app --port 8200
```

Frontend:

```bash
cd frontend
python3 -m http.server 3000
```

## Demo

Frontend:
https://cxmzt2s2w5-eng.github.io/fitness-diary/

Backend services are prepared for Render deployment through `render.yaml`.
