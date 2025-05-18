"""Phase 3 app - includes authentication"""

import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text


# Configuration
class Settings(BaseSettings):
    database_url: Optional[str] = None
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    class Config:
        env_file = ".env"
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jwt_secret = os.getenv("JWT_SECRET", self.jwt_secret)


# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: int
    email: str
    username: str


# Initialize
settings = Settings()
app = FastAPI(title="Ultra Phase 3", version="3.0.0")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Simple in-memory user store for MVP
users_db = {}


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


# Endpoints
@app.get("/")
def root():
    return {"status": "alive", "phase": 3}


@app.get("/health")
def health():
    return {"status": "ok", "services": ["api", "auth"]}


@app.get("/health/database")
def health_database():
    """Check database connectivity"""
    if not settings.database_url:
        return {
            "status": "warning",
            "message": "No database URL configured",
            "database": "not_configured",
        }

    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "connection_failed", "error": str(e)}


@app.post("/auth/register", response_model=User)
def register(user: UserRegister):
    """Register a new user"""
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    user_id = len(users_db) + 1

    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
    }

    return User(id=user_id, email=user.email, username=user.username)


@app.post("/auth/login", response_model=Token)
def login(user: UserLogin):
    """Login user and return JWT token"""
    db_user = users_db.get(user.email)

    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)


@app.get("/auth/verify")
def verify_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
):
    """Verify JWT token"""
    token_data = verify_token(credentials)
    return {"valid": True, "email": token_data.get("sub")}


@app.get("/protected")
def protected_route(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
):
    """Example protected endpoint"""
    token_data = verify_token(credentials)
    email = token_data.get("sub")
    user = users_db.get(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "message": "This is a protected endpoint",
        "user": User(id=user["id"], email=user["email"], username=user["username"]),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))  # nosec # noqa
