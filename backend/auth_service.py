import os
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User

load_dotenv()

JWT_SECRET = (os.getenv("JWT_SECRET") or "").strip()
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set or empty. "
        "Generate one with: python3 -c \"import secrets; print(secrets.token_urlsafe(64))\" "
        "and set it in backend/.env before starting the server."
    )
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
USERNAME_MIN = 3
USERNAME_MAX = 30
PASSWORD_MIN = 8


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def validate_signup(username: str, email: str, password: str) -> None:
    if not username or len(username.strip()) < USERNAME_MIN:
        raise HTTPException(status_code=400, detail=f"Username must be at least {USERNAME_MIN} characters")
    if len(username.strip()) > USERNAME_MAX:
        raise HTTPException(status_code=400, detail=f"Username must be at most {USERNAME_MAX} characters")
    if not re.match(r"^[a-zA-Z0-9_]+$", username.strip()):
        raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, and underscores")
    if not email or not EMAIL_RE.match(email.strip()):
        raise HTTPException(status_code=400, detail="Please enter a valid email address")
    if not password or len(password) < PASSWORD_MIN:
        raise HTTPException(status_code=400, detail=f"Password must be at least {PASSWORD_MIN} characters")


def signup_user(db: Session, username: str, email: str, password: str) -> User:
    username = username.strip()
    email = email.strip().lower()

    validate_signup(username, email, password)

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="This username is already taken")

    user = User(
        username=username,
        email=email,
        name=username,
        password_hash=hash_password(password),
        provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user


def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = verify_token(token)
    except HTTPException:
        return None
    return db.query(User).filter(User.id == payload["sub"]).first()


def get_current_user_required(
    request: Request, db: Session = Depends(get_db)
) -> User:
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
