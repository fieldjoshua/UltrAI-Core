"""Development app with minimal dependencies and fast startup"""

# Load environment variables FIRST before any other imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Optional: lightweight logger
try:
    from app.utils.logging import get_logger
    logger = get_logger("dev_app")
except Exception:  # pragma: no cover
    import logging
    logger = logging.getLogger("dev_app")
    logging.basicConfig(level=logging.INFO)

# FastAPI app
app = FastAPI(title="UltraAI Development", version="1.0.0-dev")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "environment": "development",
        "features": {
            "database": False,
            "auth": False,
            "caching": False,
            "frontend": True
        }
    }

@app.get("/")
async def serve_frontend():
    """Serve development frontend with enhanced cyberpunk styling"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ultra AI - Development</title>
        <style>
            body { 
                margin: 0; 
                font-family: 'Orbitron', 'Arial', monospace; 
                background: linear-gradient(135deg, #0a0f1c 0%, #1a2332 100%);
                color: #00FFFF;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .grid-bg {
                position: absolute;
                inset: 0;
                opacity: 0.1;
                background-image: 
                    linear-gradient(rgba(0, 255, 255, 0.5) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 255, 255, 0.5) 1px, transparent 1px);
                background-size: 50px 50px;
                animation: pulse 4s ease-in-out infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 0.1; }
                50% { opacity: 0.3; }
            }
            .container {
                text-align: center;
                padding: 2rem;
                z-index: 10;
                position: relative;
            }
            h1 {
                font-size: clamp(3rem, 8vw, 6rem);
                text-shadow: 
                    0 0 10px #00FFFF,
                    0 0 20px #00FFFF,
                    0 0 30px #00FFFF;
                margin-bottom: 1rem;
                letter-spacing: 0.1em;
                animation: neon-pulse 2s ease-in-out infinite;
            }
            @keyframes neon-pulse {
                0%, 100% {
                    text-shadow: 
                        0 0 10px #00FFFF,
                        0 0 20px #00FFFF,
                        0 0 30px #00FFFF;
                }
                50% {
                    text-shadow: 
                        0 0 20px #00FFFF,
                        0 0 30px #00FFFF,
                        0 0 40px #00FFFF,
                        0 0 50px #00FFFF;
                }
            }
            .tagline {
                font-size: clamp(1rem, 3vw, 1.5rem);
                color: #FF6B35;
                text-shadow: 
                    0 0 10px #FF6B35,
                    0 0 20px #FF6B35;
                margin-bottom: 2rem;
                letter-spacing: 0.05em;
            }
            .status {
                color: #FFA500;
                font-size: 1.2rem;
                margin-bottom: 2rem;
                text-shadow: 0 0 10px #FFA500;
            }
            .env-badge {
                background: rgba(255, 165, 0, 0.2);
                border: 2px solid #FFA500;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                margin-bottom: 2rem;
                display: inline-block;
            }
            .links {
                display: flex;
                gap: 2rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            .link {
                color: #00FFFF;
                text-decoration: none;
                padding: 0.8rem 1.5rem;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                transition: all 0.3s ease;
                background: rgba(0, 255, 255, 0.1);
                backdrop-filter: blur(10px);
            }
            .link:hover {
                background: rgba(0, 255, 255, 0.2);
                box-shadow: 
                    0 0 20px rgba(0, 255, 255, 0.4),
                    inset 0 0 20px rgba(0, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            @media (max-width: 768px) {
                .links { flex-direction: column; align-items: center; }
                .container { padding: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="container">
            <h1>ULTRA AI</h1>
            <div class="tagline">MULTIPLY YOUR AI!</div>
            <div class="env-badge">🚀 DEVELOPMENT MODE</div>
            <div class="status">⚡ Fast Development Server</div>
            <div class="links">
                <a href="/health" class="link">Health Check</a>
                <a href="/docs" class="link">API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Minimal static serving and API routes for local smoke tests ---

try:
    # Serve built frontend assets if available
    frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount(
            "/assets",
            StaticFiles(directory=os.path.join(frontend_dist, "assets")),
            name="assets",
        )

        @app.get("/wizard_steps.json")
        async def serve_wizard_steps_json():
            try:
                json_file = os.path.join(frontend_dist, "wizard_steps.json")
                if os.path.exists(json_file):
                    return FileResponse(json_file, media_type="application/json")
                return JSONResponse({"error": "wizard_steps.json not found"}, status_code=404)
            except Exception as exc:  # safety
                logger.error("Failed to serve wizard_steps.json", exc_info=True)
                return JSONResponse({"error": str(exc)}, status_code=500)

    # Include model availability routes at /api for quick checks
    try:
        from app.routes.model_availability_routes import router as model_availability_router
        app.include_router(model_availability_router, prefix="/api")
        logger.info("Model availability routes mounted under /api")
    except Exception:
        logger.warning("Model availability routes not available in dev app", exc_info=True)

    # Include admin routes for local testing
    try:
        from app.routes.admin_routes import router as admin_router
        app.include_router(admin_router, prefix="/api")
        logger.info("Admin routes mounted under /api")
    except Exception:
        logger.warning("Admin routes not available in dev app", exc_info=True)
except Exception:
    logger.warning("Failed to initialize dev static/API helpers", exc_info=True)

@app.get("/api/mock")
async def mock_endpoint():
    """Mock API endpoint for development testing"""
    return {
        "message": "Development API endpoint",
        "environment": "development",
        "features": ["frontend", "basic_api"],
        "note": "Database and auth disabled for faster startup"
    }