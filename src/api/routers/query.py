from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from src.core.query_processor import (
    QueryProcessor,
    QueryRequest,
    QueryResponse,
    LLMModel,
    AnalysisType,
)
from src.core.auth import get_current_user

router = APIRouter()
query_processor = QueryProcessor()
current_user_dependency = Depends(get_current_user)


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest, current_user: dict = current_user_dependency
):
    """
    Process a query with selected models and analysis type.

    Args:
        request: QueryRequest containing the query, selected models, and analysis type
        current_user: Current authenticated user

    Returns:
        QueryResponse containing the processed results and analysis
    """
    try:
        response = await query_processor.process_query(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/query/async")
async def process_query_async(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = current_user_dependency,
):
    """
    Process a query asynchronously with selected models and analysis type.

    Args:
        request: QueryRequest containing the query, selected models, and analysis type
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user

    Returns:
        Status message indicating the query is being processed
    """
    try:
        # Add the query processing task to background tasks
        background_tasks.add_task(query_processor.process_query, request)

        return {
            "status": "processing",
            "message": f"Processing query with {len(request.selected_models) or 1} models",
            "query": (
                request.query[:50] + "..." if len(request.query) > 50 else request.query
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/models", response_model=List[str])
async def get_available_models():
    """
    Get list of available LLM models.

    Returns:
        List of available model names
    """
    return [model.value for model in LLMModel]


@router.get("/analysis-types", response_model=List[str])
async def get_analysis_types():
    """
    Get list of available analysis types.

    Returns:
        List of available analysis types
    """
    return [analysis_type.value for analysis_type in AnalysisType]
