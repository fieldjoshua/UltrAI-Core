"""
Simple test endpoint to debug the middleware issue
"""

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
router = APIRouter()

@router.get("/test/simple")
async def simple_test():
    """Simple endpoint that just returns a dict"""
    return {"status": "ok", "message": "Simple test"}

@router.get("/test/models")
async def test_models():
    """Test endpoint similar to orchestrator models"""
    return {
        "status": "success",
        "models": ["model1", "model2", "model3"]
    }

# Include the router
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    # Run on a different port to avoid conflicts
    uvicorn.run(app, host="0.0.0.0", port=8082)