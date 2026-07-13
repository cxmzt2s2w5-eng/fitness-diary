import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from .database import Base, User, connection, get_db

app = FastAPI(title="Auth Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
key = os.getenv("SECRET_KEY")
if key is None:
    raise RuntimeError("SECRET_KEY is missing. Add it to auth-service/.env")

alg = "HS256"
time = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
Base.metadata.create_all(bind=connection)
def hash_password(password: str):
    return CryptContext(
        schemes=["pbkdf2_sha256"],
        deprecated="auto"
    ).hash(password)
def verify_password(plain_password: str, hashed_password: str):
    return CryptContext(
        schemes=["pbkdf2_sha256"],
        deprecated="auto"
    ).verify(plain_password, hashed_password)

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)): 
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User registered successfully",
        "user": {
            "name": new_user.name,
            "email": new_user.email
        }
    }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )
    access_token = create_access_token(
        data={"sub": existing_user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_current_user(current_token = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    i = db.query(User).filter(User.email == payload).first()
    if i is not None:
        current_user = {
            "email": payload,
            "name": i.name
        }
        return current_user

    raise HTTPException(
        status_code=401,
        detail="User not found"
    )

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=time
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key,
        algorithm=alg
    )
    return encoded_jwt

@app.get("/me")
def me(current_user = Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "name": current_user["name"]
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }
