from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.routes.health_routes import router as health_router
from app.routes.user_routes import user_router


def create_app() -> FastAPI:
    """Create a minimal FastAPI application with health and user routes."""
    app = FastAPI()
    # Include initial routers
    app.include_router(health_router)
    app.include_router(user_router, prefix="/api")
    # Include all main application routers
    from app.routes.auth_routes import auth_router
    from app.routes.document_routes import document_router
    from app.routes.analyze_routes import analyze_router
    from app.routes.orchestrator_minimal import router as orchestrator_router
    from app.routes.llm_routes import llm_router
    from app.routes.document_analysis_routes import document_analysis_router
    from app.routes.docker_modelrunner_routes import router as docker_modelrunner_router
    from app.routes.available_models_routes import router as available_models_router
    from app.routes.pricing_routes import pricing_router
    from app.routes.oauth_routes import oauth_router
    from app.routes.recovery_routes import recovery_router
    from app.routes.debug_routes import router as debug_router
    from app.routes.metrics import metrics_router

    # Register API routers under /api prefix
    api_prefix = "/api"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(document_router, prefix=api_prefix)
    app.include_router(analyze_router, prefix=api_prefix)
    app.include_router(orchestrator_router, prefix=api_prefix)
    app.include_router(llm_router, prefix=api_prefix)
    app.include_router(document_analysis_router, prefix=api_prefix)
    app.include_router(docker_modelrunner_router, prefix=api_prefix)
    app.include_router(available_models_router, prefix=api_prefix)
    app.include_router(pricing_router, prefix=api_prefix)
    app.include_router(oauth_router, prefix=api_prefix)
    app.include_router(recovery_router, prefix=api_prefix)
    app.include_router(debug_router, prefix=api_prefix)
    app.include_router(metrics_router, prefix=api_prefix)
    
    # Serve frontend static files
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/static", StaticFiles(directory=frontend_dist), name="static")
        
        @app.get("/")
        async def serve_frontend():
            """Serve the React frontend"""
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return FileResponse(index_file)
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}
        
        @app.get("/{path:path}")
        async def serve_frontend_routes(path: str):
            """Serve React app for all non-API routes (SPA routing)"""
            # Don't intercept API routes
            if path.startswith("api/") or path.startswith("docs") or path.startswith("health"):
                return {"error": "Route not found"}
            
            # Serve index.html for all other routes (React Router handles client-side routing)
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return FileResponse(index_file)
            return {"message": "Frontend not built"}
    
    return app
