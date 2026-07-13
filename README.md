# Fitness Diary

Minimal fullstack fitness diary project.

## Architecture

- `frontend` - HTML/CSS/JavaScript client
- `backend/auth-service` - FastAPI service for register, login, JWT, current user
- `backend/diary-service` - FastAPI service for diary entries
- Supabase PostgreSQL - cloud database

## Local URLs

- Frontend: `http://127.0.0.1:3000`
- Auth API docs: `http://127.0.0.1:8100/docs`
- Diary API docs: `http://127.0.0.1:8200/docs`

## Local Run

Auth service:

```bash
cd backend/auth-service
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m uvicorn app.main:app --port 8100
```

Diary service:

```bash
cd backend/diary-service
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m uvicorn app.main:app --port 8200
```

Frontend:

```bash
cd frontend
python3 -m http.server 3000
```

## Environment

Create `.env` files from `.env.example` inside both backend services.

Do not commit `.env` files to GitHub.
