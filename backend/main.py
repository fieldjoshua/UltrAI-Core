from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import os
import json
import uuid
import tempfile
from datetime import datetime
import sys
import traceback
import multiprocessing
import time
import psutil
from fastapi.responses import JSONResponse
import uvicorn
import logging
from ultra_documents_optimized import OptimizedDocumentProcessor
from pricing_simulator import PricingSimulator
from pricing_integration import PricingIntegration, track_request_cost, check_request_authorization

# Add parent directory to path to access Ultra modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ultra_pattern_orchestrator import PatternOrchestrator

# Import optimized document processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ultra_documents_optimized

# Create the temp directory for file uploads if it doesn't exist
os.makedirs("temp_uploads", exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ultra_api")

app = FastAPI(
    title="Ultra Framework API",
    description="API for the Ultra Framework orchestrating multiple LLMs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", 
                  "http://localhost:3003", "http://localhost:3004", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global performance metrics
performance_metrics = {
    "requests_processed": 0,
    "documents_processed": 0,
    "avg_processing_time": 0,
    "total_processing_time": 0,
    "max_memory_usage": 0,
    "total_chunks_processed": 0,
    "cache_hits": 0,
    "current_memory_usage_mb": 0,
    "start_time": datetime.now().isoformat()
}

# Add metrics history for time-series data
metrics_history = {
    "timestamps": [],
    "memory_usage": [],
    "cpu_usage": [],
    "requests_processed": [],
    "avg_processing_time": [],
    "documents_processed": [],
    "chunks_processed": []
}

# Maximum history points to store
MAX_HISTORY_POINTS = 100

# Create a shared document processor instance for better resource management
doc_processor = None

# Initialize document processor
document_processor = OptimizedDocumentProcessor()

# Initialize pricing system
pricing_simulator = PricingSimulator()
pricing_integration = PricingIntegration(
    pricing_simulator=pricing_simulator,
    pricing_enabled=False,  # Initially disabled, can be toggled through API
    default_tier="basic",
    usage_log_file="logs/token_usage_log.jsonl"
)
pricing_integration.load_user_accounts()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Performance metrics tracking
start_time = time.time()
requests_processed = 0
processing_times = []
max_memory_usage = 0

# Request models
class AnalyzeRequest(BaseModel):
    prompt: str
    selectedModels: List[str]
    ultraModel: str
    pattern: Optional[str] = "Confidence Analysis"
    options: Optional[Dict[str, Any]] = {}
    userId: Optional[str] = None

class TokenEstimateRequest(BaseModel):
    prompt: str
    model: str
    requestType: str = "completion"
    userId: Optional[str] = None

class PricingToggleRequest(BaseModel):
    enabled: bool
    reason: Optional[str] = None

class UserAccountRequest(BaseModel):
    userId: str
    tier: str = "basic"
    initialBalance: float = 0.0

class AddFundsRequest(BaseModel):
    userId: str
    amount: float
    description: str = "Deposit"

# Function to update metrics history
def update_metrics_history():
    """Update the metrics history with current values"""
    global metrics_history, performance_metrics, MAX_HISTORY_POINTS
    
    # Get current timestamp
    now = datetime.now().isoformat()
    
    # Get current CPU and memory usage
    current_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    current_cpu = psutil.Process().cpu_percent(interval=0.1)
    
    # Update performance metrics with current memory usage
    performance_metrics["current_memory_usage_mb"] = current_memory
    
    # Update history with current metrics
    metrics_history["timestamps"].append(now)
    metrics_history["memory_usage"].append(current_memory)
    metrics_history["cpu_usage"].append(current_cpu)
    metrics_history["requests_processed"].append(performance_metrics["requests_processed"])
    metrics_history["avg_processing_time"].append(performance_metrics["avg_processing_time"])
    metrics_history["documents_processed"].append(performance_metrics["documents_processed"])
    metrics_history["chunks_processed"].append(performance_metrics["total_chunks_processed"])
    
    # Trim history to maximum points
    if len(metrics_history["timestamps"]) > MAX_HISTORY_POINTS:
        for key in metrics_history:
            metrics_history[key] = metrics_history[key][-MAX_HISTORY_POINTS:]

def get_document_processor(reset=False):
    """Get a shared document processor instance with optimized settings"""
    global doc_processor
    
    if doc_processor is None or reset:
        # Determine optimal thread count based on available CPU cores
        cpu_count = multiprocessing.cpu_count()
        recommended_workers = max(1, cpu_count - 1)  # Leave one core free for the system
        
        doc_processor = ultra_documents_optimized.UltraDocumentsOptimized(
            cache_enabled=True,
            chunk_size=1200,  # Slightly larger chunks for better context
            chunk_overlap=150,  # 12.5% overlap for semantic continuity
            embedding_model="all-MiniLM-L6-v2",  # Efficient embedding model
            max_workers=recommended_workers,
            memory_cache_size=200  # Larger memory cache for better performance
        )
    
    return doc_processor

class PromptRequest(BaseModel):
    prompt: str
    selectedModels: List[str]
    ultraModel: str
    pattern: str = "Confidence Analysis"
    options: dict = {
        "keepDataPrivate": False,
        "useNoTraceEncryption": False
    }

class DocumentChunk(BaseModel):
    text: str
    relevance: float
    page: Optional[int] = None

class ProcessedDocument(BaseModel):
    id: str
    name: str
    chunks: List[DocumentChunk]
    totalChunks: int
    type: str

@app.options("/api/analyze")
async def options_analyze():
    return Response(status_code=200)

@app.options("/api/upload-files")
async def options_upload_files():
    return Response(status_code=200)

@app.options("/api/analyze-with-docs")
async def options_analyze_with_docs():
    return Response(status_code=200)

@app.post("/api/analyze")
async def analyze_prompt(request: PromptRequest):
    start_time = time.time()
    try:
        # Map pattern names from frontend to backend
        pattern_map = {
            "Confidence Analysis": "confidence",
            "Critique": "critique",
            "Gut Check": "gut",
            "Fact Check": "fact_check",
            "Perspective Analysis": "perspective",
            "Scenario Analysis": "scenario"
        }
        
        # Mock API keys for demo
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "perplexity": os.getenv("PERPLEXITY_API_KEY", ""),
            "cohere": os.getenv("COHERE_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "mistral": os.getenv("MISTRAL_API_KEY", "")
        }
        
        # Convert the pattern name to the format expected by the backend
        backend_pattern = pattern_map.get(request.pattern, "confidence")
        
        orchestrator = PatternOrchestrator(
            api_keys=api_keys,
            pattern=backend_pattern
        )
        
        # Set the selected models
        orchestrator.available_models = request.selectedModels
        orchestrator.ultra_model = request.ultraModel
        
        results = await orchestrator.orchestrate_full_process(request.prompt)
        
        # Update performance metrics
        global performance_metrics
        processing_time = time.time() - start_time
        performance_metrics["requests_processed"] += 1
        performance_metrics["total_processing_time"] += processing_time
        performance_metrics["avg_processing_time"] = (
            performance_metrics["total_processing_time"] / performance_metrics["requests_processed"]
        )
        performance_metrics["max_memory_usage"] = max(
            performance_metrics["max_memory_usage"],
            psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        )
        
        return {
            "status": "success",
            "data": results,
            "output_directory": orchestrator.current_session_dir,
            "processing_time": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-files")
async def upload_files(
    files: List[UploadFile] = File(...),
):
    start_time = time.time()
    try:
        # Get the optimized document processor
        document_processor = get_document_processor()
        
        processed_documents = []
        temp_paths = []
        
        try:
            # First save all files to temp directory
            for file in files:
                file_id = str(uuid.uuid4())
                # Get the file extension
                extension = os.path.splitext(file.filename)[1].lower()
                
                # Create a temporary file with the same extension
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir="temp_uploads") as temp_file:
                    # Write the uploaded file content to the temp file
                    content = await file.read()
                    temp_file.write(content)
                    temp_paths.append((temp_file.name, file_id, file.filename, file.content_type or extension[1:].upper()))
            
            # Process files in parallel using the improved processor
            file_paths = [path for path, _, _, _ in temp_paths]
            chunked_docs = document_processor.chunk_documents(file_paths)
            
            # Group chunks by file
            chunks_by_file = {}
            for chunk in chunked_docs:
                source = chunk.get("source")
                if source not in chunks_by_file:
                    chunks_by_file[source] = []
                chunks_by_file[source].append(chunk)
            
            # Create processed documents
            for temp_path, file_id, filename, content_type in temp_paths:
                if temp_path in chunks_by_file:
                    file_chunks = chunks_by_file[temp_path]
                    
                    # Convert to the expected format
                    doc_chunks = []
                    for chunk in file_chunks:
                        # Create document chunk with improved relevance scoring
                        doc_chunks.append(DocumentChunk(
                            text=chunk["text"],
                            relevance=1.0,  # Default relevance (will be updated during query time)
                            page=chunk.get("page")
                        ))
                    
                    processed_documents.append(ProcessedDocument(
                        id=file_id,
                        name=filename,
                        chunks=doc_chunks,
                        totalChunks=len(file_chunks),
                        type=content_type
                    ))
                    
                    # Update performance metrics
                    global performance_metrics
                    performance_metrics["documents_processed"] += 1
                    performance_metrics["total_chunks_processed"] += len(file_chunks)
                
        except Exception as e:
            # Log the specific error for debugging
            print(f"Error processing files: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
        
        finally:
            # Clean up the temp files
            for temp_path, _, _, _ in temp_paths:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
        
        # Update performance metrics
        processing_time = time.time() - start_time
        performance_metrics["total_processing_time"] += processing_time
        performance_metrics["max_memory_usage"] = max(
            performance_metrics["max_memory_usage"],
            psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        )
        
        return {
            "status": "success", 
            "documents": processed_documents,
            "processing_time": processing_time
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-with-docs")
async def analyze_with_docs(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    selectedModels: str = Form(...),
    ultraModel: str = Form(...),
    files: List[UploadFile] = File([]),
    pattern: str = Form("Confidence Analysis"),
    options: str = Form("{}"),
    userId: str = Form(None)
):
    start_time = time.time()
    try:
        # Parse the JSON strings
        selected_models = json.loads(selectedModels)
        options_dict = json.loads(options)
        
        # Map pattern names from frontend to backend
        pattern_map = {
            "Confidence Analysis": "confidence",
            "Critique": "critique",
            "Gut Check": "gut",
            "Fact Check": "fact_check",
            "Perspective Analysis": "perspective",
            "Scenario Analysis": "scenario"
        }
        
        # Convert the pattern name to the format expected by the backend
        backend_pattern = pattern_map.get(pattern, "confidence")
        
        # Get the optimized document processor
        document_processor = get_document_processor()
        
        # Process all files and get relevant chunks
        all_chunks = []
        processed_file_names = []
        temp_paths = []
        
        try:
            # First save all files to temp directory
            for file in files:
                # Get the file extension
                extension = os.path.splitext(file.filename)[1].lower()
                processed_file_names.append(file.filename)
                
                # Create a temporary file with the same extension
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir="temp_uploads") as temp_file:
                    # Write the uploaded file content to the temp file
                    content = await file.read()
                    temp_file.write(content)
                    temp_paths.append((temp_file.name, file.filename))
            
            # Process files in parallel for better performance
            file_paths = [path for path, _ in temp_paths]
            all_chunks = document_processor.chunk_documents(file_paths)
            
            # Add source info to each chunk
            for i, (temp_path, filename) in enumerate(temp_paths):
                for chunk in all_chunks:
                    if chunk.get("source") == temp_path:
                        chunk["source"] = filename
            
        except Exception as e:
            # Log the error
            print(f"Error processing files: {str(e)}")
            traceback.print_exc()
            
            # Clean up the temp files
            for temp_path, _ in temp_paths:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
        
        finally:
            # Clean up the temp files
            for temp_path, _ in temp_paths:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No valid content could be extracted from the provided files.")
        
        # Get relevant chunks for the query - increased for more comprehensive context
        relevant_chunks = await document_processor.get_relevant_chunks(prompt, all_chunks, top_k=10)
        
        # Create an enriched prompt with the document context - improved formatting
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            source = chunk.get("source", "Unknown")
            page = f"page {chunk.get('page')}" if chunk.get("page") is not None else "unknown page"
            # Format with relevance score in percentage
            context_parts.append(
                f"[Document {i+1}] {source} (Relevance: {chunk['relevance']*100:.1f}%)\n"
                f"```\n{chunk['text']}\n```"
            )
        
        context = "\n\n".join(context_parts)
        
        enriched_prompt = (
            f"# Query\n{prompt}\n\n"
            f"# Document Context\nThe following are relevant excerpts from the provided documents:\n\n{context}\n\n"
            f"# Instructions\nBased on the provided document context, please answer the query thoroughly and accurately. "
            f"Cite specific information from the documents when applicable. If the documents don't contain "
            f"sufficient information to fully answer the query, clearly state what information is missing."
        )
        
        # Mock API keys for demo
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "perplexity": os.getenv("PERPLEXITY_API_KEY", ""),
            "cohere": os.getenv("COHERE_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "mistral": os.getenv("MISTRAL_API_KEY", "")
        }
        
        # Initialize the orchestrator
        orchestrator = PatternOrchestrator(
            api_keys=api_keys,
            pattern=backend_pattern
        )
        
        # Set the selected models
        orchestrator.available_models = selected_models
        orchestrator.ultra_model = ultraModel
        
        # Run the analysis with the enriched prompt
        results = await orchestrator.orchestrate_full_process(enriched_prompt)
        
        # Add document metadata to the response
        doc_metadata = {
            "documents_used": processed_file_names,
            "chunks_used": len(relevant_chunks),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update performance metrics
        global performance_metrics
        processing_time = time.time() - start_time
        performance_metrics["requests_processed"] += 1
        performance_metrics["documents_processed"] += len(processed_file_names)
        performance_metrics["total_chunks_processed"] += len(all_chunks)
        performance_metrics["total_processing_time"] += processing_time
        performance_metrics["avg_processing_time"] = (
            performance_metrics["total_processing_time"] / performance_metrics["requests_processed"]
        )
        performance_metrics["max_memory_usage"] = max(
            performance_metrics["max_memory_usage"],
            psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        )
        
        return {
            "status": "success",
            "data": results,
            "document_metadata": doc_metadata,
            "output_directory": orchestrator.current_session_dir,
            "processing_time": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def check_status():
    try:
        return {"status": "operational"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Get current performance metrics"""
    try:
        global performance_metrics
        
        # Add current memory usage and update history
        update_metrics_history()
        
        # Add cache stats if available
        cache_stats = {}
        document_processor = get_document_processor()
        if document_processor and document_processor.cache_enabled:
            memory_cache_size = document_processor.cache.memory_cache.size()
            cache_stats["memory_cache_size"] = memory_cache_size
        
        # Calculate uptime
        start_time = datetime.fromisoformat(performance_metrics["start_time"])
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        
        # Prepare detailed metrics response
        metrics = {
            **performance_metrics,
            "uptime_seconds": uptime_seconds,
            "cache_stats": cache_stats
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

@app.get("/api/metrics/history")
async def get_metrics_history():
    """Get historical metrics data for time-series visualization"""
    try:
        global metrics_history
        
        # Update history with current values before returning
        update_metrics_history()
        
        return metrics_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics history: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and Docker health checks"""
    try:
        # Check if we can initialize our main classes as a basic health check
        from ultra_pattern_orchestrator import PatternOrchestrator
        
        # Get memory usage
        memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        
        # Get CPU usage
        cpu_percent = psutil.Process().cpu_percent(interval=0.1)
        
        # Check disk space
        disk_usage = psutil.disk_usage('/')
        
        # System information
        system_info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "cpu_count": multiprocessing.cpu_count(),
            "memory_total": psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
        }
        
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "system_info": system_info,
            "metrics": {
                "memory_usage_mb": memory_usage,
                "cpu_percent": cpu_percent,
                "disk_usage_percent": disk_usage.percent,
                "requests_processed": performance_metrics["requests_processed"],
                "documents_processed": performance_metrics["documents_processed"],
                "avg_processing_time": performance_metrics["avg_processing_time"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

# Cleanup handler
@app.on_event("shutdown")
def shutdown_event():
    """Clean up resources on shutdown"""
    document_processor = get_document_processor()
    if document_processor:
        document_processor.cleanup()

# Health check endpoint
@app.get("/api/health")
async def health_check():
    uptime = time.time() - start_time
    memory_info = psutil.Process(os.getpid()).memory_info()
    current_memory = memory_info.rss / (1024 * 1024)  # Convert to MB
    
    global max_memory_usage
    max_memory_usage = max(max_memory_usage, current_memory)
    
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "requests_processed": requests_processed,
        "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
        "current_memory_mb": current_memory,
        "max_memory_mb": max_memory_usage,
        "pricing_enabled": pricing_integration.pricing_enabled
    }

# Existing analyze endpoint - updated with pricing
@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    global requests_processed, processing_times
    start_process_time = time.time()
    
    # Generate a session ID for this request
    session_id = str(uuid.uuid4())
    
    # Estimate token usage and check authorization if pricing is enabled
    estimated_tokens = len(request.prompt.split()) * 4  # Simple estimate
    
    if pricing_integration.pricing_enabled and request.userId:
        auth_result = await check_request_authorization(
            price_integration=pricing_integration,
            user_id=request.userId,
            model=request.ultraModel,
            estimated_tokens=estimated_tokens,
            request_type="completion"
        )
        
        if not auth_result["authorized"]:
            return JSONResponse(
                status_code=402,  # Payment Required
                content={
                    "status": "error",
                    "message": auth_result["reason"],
                    "estimated_cost": auth_result.get("estimated_cost", 0),
                    "current_balance": auth_result.get("current_balance", 0)
                }
            )
    
    try:
        # Process the request with your existing logic
        # This is a placeholder for your actual processing logic
        response = {
            "result": f"Processed prompt: {request.prompt[:50]}...",
            "selectedModels": request.selectedModels,
            "ultraModel": request.ultraModel,
            "pattern": request.pattern,
            "processing_time": time.time() - start_process_time,
            "session_id": session_id
        }
        
        # Update metrics
        requests_processed += 1
        processing_time = time.time() - start_process_time
        processing_times.append(processing_time)
        
        # Track token usage in background to not block the response
        background_tasks.add_task(
            track_token_usage_background,
            user_id=request.userId or "anonymous",
            model=request.ultraModel,
            token_count=estimated_tokens * 2,  # Actual tokens used (would be calculated more precisely)
            session_id=session_id
        )
        
        return {
            "status": "success",
            "result": response,
            "metrics": {
                "processing_time": processing_time,
                "session_id": session_id
            }
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Token usage estimate endpoint
@app.post("/api/estimate-tokens")
async def estimate_tokens(request: TokenEstimateRequest):
    # Simple token estimation logic
    estimated_tokens = len(request.prompt.split()) * 4  # Simple estimate
    
    # Get cost estimate if pricing is enabled
    cost_estimate = {"cost": 0, "details": {}}
    
    if request.userId:
        estimate = pricing_integration.estimate_request_cost(
            user_id=request.userId,
            model=request.model,
            estimated_tokens=estimated_tokens,
            request_type=request.requestType
        )
        
        cost_estimate = {
            "cost": estimate["estimated_cost"],
            "tier": estimate["tier"],
            "has_sufficient_balance": estimate.get("has_sufficient_balance", True),
            "details": {
                "base_cost": estimate["cost_details"].get("base_cost", 0),
                "markup": estimate["cost_details"].get("markup_cost", 0),
                "discount": estimate["cost_details"].get("discount_amount", 0),
                "features": estimate["cost_details"].get("feature_costs", {})
            }
        }
    
    return {
        "prompt_length": len(request.prompt),
        "estimated_tokens": estimated_tokens,
        "model": request.model,
        "requestType": request.requestType,
        "pricing_enabled": pricing_integration.pricing_enabled,
        "cost_estimate": cost_estimate
    }

# Document processing endpoint with pricing integration
@app.post("/api/process-documents-with-pricing")
async def process_documents_with_pricing(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    selectedModels: str = Form(...),
    ultraModel: str = Form(...),
    files: List[UploadFile] = File([]),
    pattern: str = Form("Confidence Analysis"),
    options: str = Form("{}"),
    userId: str = Form(None)
):
    global requests_processed, processing_times
    start_process_time = time.time()
    
    # Generate a session ID for this request
    session_id = str(uuid.uuid4())
    
    # Parse JSON strings
    try:
        selected_models = json.loads(selectedModels)
        options_dict = json.loads(options)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON in selectedModels or options"}
        )
    
    # Estimate token usage and check authorization if pricing is enabled
    # Calculate a base token estimate from prompt + additional for each document
    base_token_estimate = len(prompt.split()) * 4
    doc_token_estimate = sum([5000 for _ in files])  # Rough estimate per document
    estimated_tokens = base_token_estimate + doc_token_estimate
    
    if pricing_integration.pricing_enabled and userId:
        auth_result = await check_request_authorization(
            price_integration=pricing_integration,
            user_id=userId,
            model=ultraModel,
            estimated_tokens=estimated_tokens,
            request_type="document_processing"
        )
        
        if not auth_result["authorized"]:
            return JSONResponse(
                status_code=402,  # Payment Required
                content={
                    "status": "error",
                    "message": auth_result["reason"],
                    "estimated_cost": auth_result.get("estimated_cost", 0),
                    "current_balance": auth_result.get("current_balance", 0)
                }
            )
    
    try:
        # Process documents
        document_data = []
        for file in files:
            content = await file.read()
            # Save the file temporarily
            temp_path = f"temp/{file.filename}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(content)
            
            # Process the document
            document_data.append({
                "name": file.filename,
                "path": temp_path,
                "size": len(content)
            })
        
        # Process the request with your documents
        # This is a placeholder for your actual document processing logic
        processed_docs = document_processor.process_documents(document_data)
        
        # Process the query with documents
        response = {
            "result": f"Processed prompt with {len(files)} documents: {prompt[:50]}...",
            "selectedModels": selected_models,
            "ultraModel": ultraModel,
            "pattern": pattern,
            "document_metadata": {
                "file_count": len(files),
                "chunks_used": processed_docs.get("chunks_processed", 0),
                "total_tokens": estimated_tokens
            },
            "processing_time": time.time() - start_process_time,
            "session_id": session_id
        }
        
        # Update metrics
        requests_processed += 1
        processing_time = time.time() - start_process_time
        processing_times.append(processing_time)
        
        # Track token usage in background
        background_tasks.add_task(
            track_token_usage_background,
            user_id=userId or "anonymous",
            model=ultraModel,
            token_count=estimated_tokens,
            request_type="document_processing",
            session_id=session_id
        )
        
        # Clean up temp files in background
        background_tasks.add_task(cleanup_temp_files, [doc["path"] for doc in document_data])
        
        return {
            "status": "success",
            "result": response,
            "document_metadata": response["document_metadata"],
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Pricing toggle endpoint (admin only)
@app.post("/api/admin/pricing/toggle")
async def toggle_pricing(request: PricingToggleRequest):
    # In a real system, you would add authentication/authorization here
    prev_state = pricing_integration.pricing_enabled
    pricing_integration.pricing_enabled = request.enabled
    
    logger.info(f"Pricing {'enabled' if request.enabled else 'disabled'}, reason: {request.reason}")
    
    return {
        "status": "success",
        "pricing_enabled": pricing_integration.pricing_enabled,
        "previous_state": prev_state,
        "message": f"Pricing has been {'enabled' if request.enabled else 'disabled'}"
    }

# User account endpoints
@app.post("/api/user/create")
async def create_user(request: UserAccountRequest):
    result = pricing_integration.create_user_account(
        user_id=request.userId,
        tier=request.tier,
        initial_balance=request.initialBalance
    )
    
    if "error" in result:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": result["error"]}
        )
    
    return {
        "status": "success",
        "user": result
    }

@app.post("/api/user/add-funds")
async def add_funds(request: AddFundsRequest):
    result = pricing_integration.add_funds(
        user_id=request.userId,
        amount=request.amount,
        description=request.description
    )
    
    if "error" in result:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": result["error"]}
        )
    
    return {
        "status": "success",
        "transaction": result
    }

@app.get("/api/user/{user_id}/balance")
async def get_user_balance(user_id: str):
    result = pricing_integration.check_balance(user_id)
    
    if "error" in result:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": result["error"]}
        )
    
    return {
        "status": "success",
        "balance": result
    }

@app.get("/api/user/{user_id}/usage")
async def get_user_usage(user_id: str):
    result = pricing_integration.get_user_usage_summary(user_id)
    
    if "error" in result and "No usage data" not in result["error"]:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": result["error"]}
        )
    
    return {
        "status": "success",
        "usage": result
    }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    result = pricing_integration.get_session_summary(session_id)
    
    if "error" in result:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": result["error"]}
        )
    
    return {
        "status": "success",
        "session": result
    }

# Background tasks
async def track_token_usage_background(
    user_id: str, 
    model: str, 
    token_count: int, 
    request_type: str = "completion",
    session_id: Optional[str] = None
):
    """Background task to track token usage"""
    await track_request_cost(
        price_integration=pricing_integration,
        user_id=user_id,
        model=model,
        token_count=token_count,
        request_type=request_type,
        session_id=session_id
    )

def cleanup_temp_files(file_paths: List[str]):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"Error removing temp file {path}: {e}")

# Run server
if __name__ == "__main__":
    # Create temp directory for document processing
    os.makedirs("temp", exist_ok=True)
    
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 