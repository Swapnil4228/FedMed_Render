from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import User
from pydantic import BaseModel

router = APIRouter()

# bcrypt has a 72-byte password limit
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


def get_password_hash(password: str) -> str:
    # ✅ FIX: truncate password safely to bcrypt limit
    safe_password = password.encode("utf-8")[:72]
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # ✅ FIX: same truncation during verification
    safe_password = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(safe_password, hashed_password)


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user.email,
        password=get_password_hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "email": db_user.email
    }
