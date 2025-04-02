from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
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

# Add parent directory to path to access Ultra modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ultra_pattern_orchestrator import PatternOrchestrator
from ultra_documents import UltraDocuments

# Create the temp directory for file uploads if it doesn't exist
os.makedirs("temp_uploads", exist_ok=True)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        return {
            "status": "success",
            "data": results,
            "output_directory": orchestrator.current_session_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-files")
async def upload_files(
    files: List[UploadFile] = File(...),
):
    try:
        document_processor = UltraDocuments(
            cache_enabled=True,
            chunk_size=1000,
            chunk_overlap=300
        )
        
        processed_documents = []
        
        for file in files:
            file_id = str(uuid.uuid4())
            # Get the file extension
            extension = os.path.splitext(file.filename)[1].lower()
            
            # Create a temporary file with the same extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir="temp_uploads") as temp_file:
                # Write the uploaded file content to the temp file
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Process the document
            try:
                chunks = await document_processor.process_document(temp_path)
                
                # Add relevance scores (for demo - would normally be calculated during analysis)
                doc_chunks = []
                for i, chunk in enumerate(chunks):
                    # Improved relevance scoring that doesn't simply decay with position
                    # This is a placeholder until we implement proper semantic relevance
                    relevance = 0.7 + (0.3 * ((len(chunks) - i) / len(chunks))) if len(chunks) > 1 else 1.0
                    
                    doc_chunks.append(DocumentChunk(
                        text=chunk["text"],
                        relevance=relevance,
                        page=chunk.get("page")
                    ))
                
                processed_documents.append(ProcessedDocument(
                    id=file_id,
                    name=file.filename,
                    chunks=doc_chunks,
                    totalChunks=len(chunks),
                    type=file.content_type or extension[1:].upper()
                ))
                
            except Exception as e:
                # Log the specific error for debugging
                print(f"Error processing {file.filename}: {str(e)}")
                traceback.print_exc()
                
                # Clean up the temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
            
            # Clean up the temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return {
            "status": "success", 
            "documents": processed_documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-with-docs")
async def analyze_with_documents(
    prompt: str = Form(...),
    selectedModels: str = Form(...),
    ultraModel: str = Form(...),
    pattern: str = Form("Confidence Analysis"),
    options: str = Form("{}"),
    files: List[UploadFile] = File(...)
):
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
        
        # Create a document processor
        document_processor = UltraDocuments(
            cache_enabled=True,
            chunk_size=1000,
            chunk_overlap=300,
            embedding_model="all-MiniLM-L6-v2"  # Lightweight but effective embedding model
        )
        
        # Process all files and get relevant chunks
        all_chunks = []
        processed_file_names = []
        
        for file in files:
            # Get the file extension
            extension = os.path.splitext(file.filename)[1].lower()
            processed_file_names.append(file.filename)
            
            # Create a temporary file with the same extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir="temp_uploads") as temp_file:
                # Write the uploaded file content to the temp file
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Process the document
            try:
                chunks = await document_processor.process_document(temp_path)
                # Add source info to each chunk
                for chunk in chunks:
                    chunk["source"] = file.filename
                all_chunks.extend(chunks)
                
            except Exception as e:
                # Log the error and continue with other files
                print(f"Error processing file {file.filename}: {str(e)}")
                traceback.print_exc()
                
                # Clean up the temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
                # We'll continue with the rest of the files instead of failing completely
                continue
            
            # Clean up the temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No valid content could be extracted from the provided files.")
        
        # Get relevant chunks for the query - increase to top 8 for more comprehensive context
        relevant_chunks = await document_processor.get_relevant_chunks(prompt, all_chunks, top_k=8)
        
        # Create an enriched prompt with the document context - improved formatting
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            source = chunk.get("source", "Unknown")
            page = f"page {chunk.get('page')}" if chunk.get("page") is not None else "unknown page"
            context_parts.append(
                f"Document {i+1}: {source} ({page}, relevance: {chunk['relevance']:.2f})\n"
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
        
        return {
            "status": "success",
            "data": results,
            "document_metadata": doc_metadata,
            "output_directory": orchestrator.current_session_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def check_status():
    try:
        return {"status": "operational"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and Docker health checks"""
    try:
        # Check if we can instantiate our main classes as a basic health check
        from ultra_pattern_orchestrator import PatternOrchestrator
        from ultra_documents import UltraDocuments
        
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}") 