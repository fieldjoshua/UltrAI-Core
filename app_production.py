"""Production-ready app with auth, database, and caching"""

import json
import os
from datetime import datetime, timedelta

import jwt
import redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Database setup
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup with error handling
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    redis_available = True
except Exception as e:
    print(f"Redis not available: {e}")
    redis_client = None
    redis_available = False


# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="user")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="documents")
    analyses = relationship("Analysis", back_populates="document")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    llm_provider = Column(String)
    prompt = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="analyses")


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="UltraAI Production API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cache decorator with fallback
def cache_result(expire_time: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not redis_available:
                return await func(*args, **kwargs)

            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
                result = await func(*args, **kwargs)
                redis_client.setex(cache_key, expire_time, json.dumps(result))
                return result
            except Exception as e:
                print(f"Cache error: {e}")
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_user(credentials: HTTPAuthorizationCredentials, db: Session):
    """Verify user from token and return user object"""
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class DocumentCreate(BaseModel):
    filename: str
    content: str


class AnalysisCreate(BaseModel):
    document_id: int
    llm_provider: str
    prompt: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str


# Endpoints
# Root route removed to allow frontend static files to be served
# The frontend is now served at the root URL
# API documentation available at /docs


@app.get("/debug/files")
async def debug_files():
    """Debug endpoint to check what files exist"""
    import os
    current_dir = os.path.dirname(__file__)
    return {
        "current_dir": current_dir,
        "root_files": os.listdir(current_dir),
        "frontend_exists": os.path.exists(os.path.join(current_dir, "frontend")),
        "frontend_contents": os.listdir(os.path.join(current_dir, "frontend")) if os.path.exists(os.path.join(current_dir, "frontend")) else None
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Check if keys are real or placeholders
    openai_is_real = openai_key and not openai_key.startswith("your_") and len(openai_key) > 20
    anthropic_is_real = anthropic_key and not anthropic_key.startswith("your_") and len(anthropic_key) > 20
    google_is_real = google_key and not google_key.startswith("your_") and len(google_key) > 20
    
    return {
        "status": "DEMO MODE - API KEYS NOT CONFIGURED" if not (openai_is_real or anthropic_is_real) else "PRODUCTION MODE",
        "openai_key_set": bool(openai_key),
        "openai_key_prefix": openai_key[:15] + "..." if openai_key else "None",
        "openai_is_real": openai_is_real,
        "anthropic_key_set": bool(anthropic_key),
        "anthropic_key_prefix": anthropic_key[:15] + "..." if anthropic_key else "None", 
        "anthropic_is_real": anthropic_is_real,
        "google_key_set": bool(google_key),
        "google_is_real": google_is_real,
        "environment": os.getenv("ENVIRONMENT", "not_set"),
        "use_mock": os.getenv("USE_MOCK", "not_set"),
        "render_instructions": "Set API keys in Render dashboard Environment tab using values from .env.render file"
    }

@app.get("/config/status")
async def config_status():
    """Check configuration status and provide guidance"""
    import os
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Check if keys are real or placeholders
    openai_is_real = openai_key and not openai_key.startswith("your_") and len(openai_key) > 20
    anthropic_is_real = anthropic_key and not anthropic_key.startswith("your_") and len(anthropic_key) > 20
    google_is_real = google_key and not google_key.startswith("your_") and len(google_key) > 20
    
    any_real_keys = openai_is_real or anthropic_is_real or google_is_real
    
    status = {
        "configured": any_real_keys,
        "mode": "PRODUCTION" if any_real_keys else "DEMO",
        "providers": {
            "openai": {"configured": openai_is_real, "available": openai_is_real},
            "anthropic": {"configured": anthropic_is_real, "available": anthropic_is_real},
            "google": {"configured": google_is_real, "available": google_is_real}
        }
    }
    
    if not any_real_keys:
        status["error"] = "⚠️ API Keys not configured - Running in DEMO mode"
        status["instructions"] = [
            "1. Go to Render Dashboard: https://dashboard.render.com/",
            "2. Select your ultrai-core service",
            "3. Go to Environment tab",
            "4. Copy API keys from your local .env.render file",
            "5. Add them as environment variables in Render",
            "6. Deploy the service"
        ]
    
    return status

@app.get("/health")
async def health():
    checks = {"api": "ok", "database": "checking", "cache": "checking"}

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    finally:
        db.close()

    # Check Redis
    if redis_available:
        try:
            redis_client.ping()
            checks["cache"] = "connected"
        except Exception as e:
            checks["cache"] = f"error: {str(e)}"
    else:
        checks["cache"] = "not configured"

    return {"status": "ok", "services": checks}


@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(id=db_user.id, email=db_user.email, username=db_user.username)


@app.post("/auth/login", response_model=TokenResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token)


@app.get("/auth/verify")
async def verify_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = verify_token(credentials)
    return {"valid": True, "email": payload.get("sub")}


@app.get("/protected")
async def protected_route(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Protected endpoint",
        "user": UserResponse(id=user.id, email=user.email, username=user.username),
    }


@app.post("/documents")
async def create_document(
    document: DocumentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_document = Document(
        user_id=user.id, filename=document.filename, content=document.content
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return {
        "id": db_document.id,
        "filename": db_document.filename,
        "created_at": db_document.created_at,
    }


@app.get("/documents")
async def list_documents(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    documents = db.query(Document).filter(Document.user_id == user.id).all()
    return [
        {"id": d.id, "filename": d.filename, "created_at": d.created_at.isoformat()}
        for d in documents
    ]


@app.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user.id)
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "filename": document.filename,
        "content": document.content,
        "created_at": document.created_at.isoformat(),
    }


@app.post("/analyses")
async def create_analysis(
    analysis: AnalysisCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Verify user owns the document
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    document = (
        db.query(Document)
        .filter(Document.id == analysis.document_id, Document.user_id == user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404, detail="Document not found or access denied"
        )

    # Check cache first
    cache_key = (
        f"analysis:{analysis.document_id}:{analysis.llm_provider}:{analysis.prompt}"
    )
    cached_response = None

    if redis_available:
        try:
            cached_response = redis_client.get(cache_key)
        except Exception as e:
            print(f"Cache get error: {e}")

    if cached_response:
        response = cached_response
    else:
        # Call actual LLM
        try:
            if analysis.llm_provider.startswith("gpt"):
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY", "")
                if not openai.api_key:
                    response = "Error: OpenAI API key not configured"
                else:
                    client = openai.OpenAI(api_key=openai.api_key)
                    completion = client.chat.completions.create(
                        model=analysis.llm_provider,
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant that analyzes documents."},
                            {"role": "user", "content": f"{analysis.prompt}\n\nDocument content:\n{document.content}"}
                        ],
                        max_tokens=1000
                    )
                    response = completion.choices[0].message.content
            elif analysis.llm_provider.startswith("claude"):
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
                if not api_key:
                    response = "Error: Anthropic API key not configured"
                else:
                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model=analysis.llm_provider,
                        max_tokens=1000,
                        messages=[
                            {"role": "user", "content": f"{analysis.prompt}\n\nDocument content:\n{document.content}"}
                        ]
                    )
                    response = message.content[0].text
            else:
                response = f"Error: Unsupported LLM provider: {analysis.llm_provider}"
        except Exception as e:
            response = f"Error calling {analysis.llm_provider}: {str(e)}"
        
        if redis_available:
            try:
                redis_client.setex(cache_key, 3600, response)
            except Exception as e:
                print(f"Cache set error: {e}")

    # Save to database
    db_analysis = Analysis(
        document_id=analysis.document_id,
        llm_provider=analysis.llm_provider,
        prompt=analysis.prompt,
        response=response,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    return {
        "id": db_analysis.id,
        "response": db_analysis.response,
        "cached": bool(cached_response),
        "created_at": db_analysis.created_at.isoformat(),
    }


@app.get("/analyses/{document_id}")
async def get_analyses(
    document_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Verify user owns the document
    payload = verify_token(credentials)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user.id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404, detail="Document not found or access denied"
        )

    analyses = db.query(Analysis).filter(Analysis.document_id == document_id).all()
    return [
        {
            "id": a.id,
            "llm_provider": a.llm_provider,
            "prompt": a.prompt,
            "response": a.response,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]


# Pydantic models for orchestrator
class OrchestratorRequest(BaseModel):
    prompt: str
    models: list[str] = ["gpt-3.5-turbo"]
    args: dict = {}
    kwargs: dict = {}


@app.post("/api/orchestrator/execute")
async def execute_orchestrator(
    request: OrchestratorRequest,
):
    """Execute orchestrator request"""
    try:
        model = request.models[0] if request.models else "gpt-3.5-turbo"
        
        if model.startswith("gpt"):
            import openai
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key or api_key.startswith("your_ope"):
                response = f"Error: OpenAI API key not configured. Found: {api_key[:20] if api_key else 'None'}..."
            else:
                client = openai.OpenAI(api_key=api_key)
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": request.prompt}
                    ],
                    max_tokens=1000
                )
                response = completion.choices[0].message.content
        elif model.startswith("claude"):
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if not api_key or len(api_key) < 10:
                response = f"Error: Anthropic API key not configured. Found: {api_key[:20] if api_key else 'None'}..."
            else:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": request.prompt}
                    ]
                )
                response = message.content[0].text
        else:
            response = f"Error: Unsupported model: {model}"
            
    except Exception as e:
        response = f"Error: {str(e)}"
    
    result = {
        "status": "success",
        "result": {
            "prompt": request.prompt,
            "models": request.models,
            "args": request.args,
            "kwargs": request.kwargs,
            "response": response,
        },
    }

    return result


@app.get("/api/available-models")
async def get_available_models():
    """Get list of available LLM models"""
    return {
        "status": "ok",
        "available_models": [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ],
    }



# Mount static files for integrated frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    try:
        # Mount static files at root with HTML fallback for SPA routing
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
        print(f"✅ Static frontend mounted from: {static_dir}")
    except (RuntimeError, FileNotFoundError) as e:
        print(f"❌ Could not mount static frontend: {e}")
else:
    print(f"⚠️ Static directory not found at: {static_dir}")
    print("Creating static directory...")
    os.makedirs(static_dir, exist_ok=True)
