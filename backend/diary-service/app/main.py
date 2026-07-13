import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import Base, DiaryEntry, connection, get_db

load_dotenv()
app = FastAPI(title="Diary Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
key = os.getenv("SECRET_KEY")
if key is None:
    raise RuntimeError("SECRET_KEY is missing. Add it to diary-service/.env")

alg = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=connection)
class DiaryEntryCreate(BaseModel):
    title: str
    content: str
    mood: str | None = None

def get_current_user_email(current_token = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            current_token,
            key,
            algorithms=[alg]
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    payload = payload.get("sub")
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    return payload

@app.post("/entries")
def create_entry(
    entry: DiaryEntryCreate,
    current_user_email = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    new_entry = DiaryEntry(
        user_email=current_user_email,
        title=entry.title,
        content=entry.content,
        mood=entry.mood
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {
        "id": new_entry.id,
        "user_email": new_entry.user_email,
        "title": new_entry.title,
        "content": new_entry.content,
        "mood": new_entry.mood,
        "created_at": new_entry.created_at
    }


@app.get("/entries")
def get_entries(
    current_user_email = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    entries = (
        db.query(DiaryEntry)
        .filter(DiaryEntry.user_email == current_user_email)
        .order_by(DiaryEntry.created_at.desc())
        .all()
    )
    return [
        {
            "id": entry.id,
            "user_email": entry.user_email,
            "title": entry.title,
            "content": entry.content,
            "mood": entry.mood,
            "created_at": entry.created_at
        }
        for entry in entries
    ]

@app.get("/health")
def health():
    return {
        "status": "ok"
    }
