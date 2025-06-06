from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Route handlers for the Ultra backend.

This module provides API routes for various endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Document management routes for the Ultra backend.

This module provides endpoints for uploading, managing, and processing documents.
Implements the multi-layered architecture described in the UltrLLMOrchestrator patent.
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses 
from app.core.error_handling import (
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
    handle_error,
)
from app.models.document import DocumentUploadResponse
from app.services.document_processor import UltraDocumentsOptimized
from app.utils.logging import get_logger

# Configure logging
logger = get_logger("document_routes")

# Set document storage path from config
DOCUMENT_STORAGE_PATH = os.getenv("DOCUMENT_STORAGE_PATH", "documents")

# Default values for document processing
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB chunks

# Default FastAPI dependencies
REQUIRED_FILE = File(...)
REQUIRED_FORM = Form(...)
EMPTY_DICT = Depends(lambda: {})


def create_router(document_processor: UltraDocumentsOptimized) -> APIRouter:
    """
    Create the document router with dependencies.

    Args:
        document_processor: The document processor instance to use for document operations

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Documents"])

    @router.post("/api/upload-document", class DocumentUploadResponse(BaseModel):
    """Response model for documentuploadresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=DocumentUploadResponse)
        """
    Create upload document.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Create a unique ID for the document
            document_id = str(uuid.uuid4())

            # Create a directory for the document
            document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
            os.makedirs(document_dir, exist_ok=True)

            # Get file name and sanitize it
            file_name = file.filename
            if not file_name:
                file_name = f"document_{document_id}"

            # Full path to save the file
            file_path = os.path.join(document_dir, file_name)

            # Save the file with error handling
            try:
                with open(file_path, "wb") as f:
                    # Read chunks to handle large files
                    while True:
                        chunk = await file.read(DEFAULT_CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
            except Exception as e:
                # Clean up on failure
                if os.path.exists(document_dir):
                    shutil.rmtree(document_dir)
                raise ServiceError(
                    message="Failed to save document",
                    details={"error": str(e)},
                )

            # Get file size
            try:
                file_size = os.path.getsize(file_path)
            except Exception as e:
                raise ServiceError(
                    message="Failed to get file size",
                    details={"error": str(e)},
                )

            # Get file extension
            file_extension = os.path.splitext(file_name)[1].lower() if file_name else ""

            # Create metadata for the document
            metadata = {
                "id": document_id,
                "original_filename": file_name,
                "file_path": file_path,
                "file_size": file_size,
                "file_type": file_extension,
                "upload_timestamp": datetime.now().isoformat(),
                "processing_status": "ready",
            }

            # Save metadata with error handling
            try:
                with open(os.path.join(document_dir, "metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                raise ServiceError(
                    message="Failed to save document metadata",
                    details={"error": str(e)},
                )

            return DocumentUploadResponse(
                id=document_id,
                name=file_name,
                size=file_size,
                type=file_extension,
                status="uploaded",
                message="Document uploaded successfully",
            )
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return handle_error(e)
        finally:
            await file.close()

    @router.get("/api/documents/{document_id}", class Dict(BaseModel):
    """Response model for dict endpoint."""
    status: str
    data: Dict[str, Any]

response_model=Dict[str, Any])
        """
    Get get document.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Check if document directory exists
            document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
            if not os.path.exists(document_dir):
                raise ResourceNotFoundError(
                    message=f"Document {document_id} not found",
                    details={"document_id": document_id},
                )

            # Check if metadata file exists
            metadata_path = os.path.join(document_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                raise ServiceError(
                    message="Document metadata not found",
                    details={"document_id": document_id},
                )

            # Read metadata
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
            except Exception as e:
                raise ServiceError(
                    message="Failed to read document metadata",
                    details={"error": str(e)},
                )

            return {
                "id": metadata["id"],
                "name": metadata.get("original_filename", "Unknown"),
                "size": metadata.get("file_size", 0),
                "type": metadata.get("file_type", ""),
                "status": metadata.get("processing_status", "unknown"),
                "uploadDate": metadata.get("upload_timestamp", ""),
            }
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return handle_error(e)

    @router.get("/api/documents", class List(BaseModel):
    """Response model for list endpoint."""
    status: str
    data: Dict[str, Any]

response_model=List[Dict[str, Any]])
        """
    Get list documents.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            documents = []

            # Check if document storage directory exists
            if not os.path.exists(DOCUMENT_STORAGE_PATH):
                return []

            # Iterate through document directories
            for document_id in os.listdir(DOCUMENT_STORAGE_PATH):
                document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)

                # Skip if not a directory
                if not os.path.isdir(document_dir):
                    continue

                # Check for metadata file
                metadata_path = os.path.join(document_dir, "metadata.json")
                if not os.path.exists(metadata_path):
                    continue

                # Read metadata with error handling
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    documents.append(
                        {
                            "id": metadata["id"],
                            "name": metadata.get("original_filename", "Unknown"),
                            "size": metadata.get("file_size", 0),
                            "type": metadata.get("file_type", ""),
                            "status": metadata.get("processing_status", "unknown"),
                            "uploadDate": metadata.get("upload_timestamp", ""),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error reading document metadata: {str(e)}")
                    continue

            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return handle_error(e)

    @router.post("/api/create-document-session")
        """
    Create create document session.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Parse request data
            body = await request.json()
            file_name = body.get("fileName", "")
            file_size = body.get("fileSize", 0)
            chunk_size = body.get("chunkSize", DEFAULT_CHUNK_SIZE)
            total_chunks = body.get("totalChunks", 0)

            # Validate inputs
            if not all([file_name, file_size, chunk_size, total_chunks]):
                raise ValidationError(
                    message="Missing required fields",
                    details={
                        "required": [
                            "fileName",
                            "fileSize",
                            "chunkSize",
                            "totalChunks",
                        ],
                        "provided": body,
                    },
                )

            # Create session ID
            session_id = str(uuid.uuid4())

            # Create session directory
            session_dir = os.path.join(DOCUMENT_STORAGE_PATH, f"temp_{session_id}")
            os.makedirs(session_dir, exist_ok=True)

            # Save session metadata
            session_metadata = {
                "session_id": session_id,
                "file_name": file_name,
                "file_size": file_size,
                "chunk_size": chunk_size,
                "total_chunks": total_chunks,
                "uploaded_chunks": [],
                "created_at": datetime.now().isoformat(),
            }

            try:
                with open(os.path.join(session_dir, "session.json"), "w") as f:
                    json.dump(session_metadata, f, indent=2)
            except Exception as e:
                raise ServiceError(
                    message="Failed to save session metadata",
                    details={"error": str(e)},
                )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "session_id": session_id,
                    "message": "Document session created successfully",
                },
            )
        except Exception as e:
            logger.error(f"Error creating document session: {str(e)}")
            return handle_error(e)

    @router.post("/api/upload-document-chunk")
        """
    Create upload document chunk.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Validate session
            session_dir = os.path.join(DOCUMENT_STORAGE_PATH, f"temp_{session_id}")
            if not os.path.exists(session_dir):
                raise ResourceNotFoundError(
                    message="Session not found",
                    details={"session_id": session_id},
                )

            # Read session metadata
            try:
                with open(os.path.join(session_dir, "session.json"), "r") as f:
                    session_metadata = json.load(f)
            except Exception as e:
                raise ServiceError(
                    message="Failed to read session metadata",
                    details={"error": str(e)},
                )

            # Save chunk
            chunk_path = os.path.join(session_dir, f"chunk_{chunk_index}")
            try:
                with open(chunk_path, "wb") as f:
                    while True:
                        chunk_data = await chunk.read(DEFAULT_CHUNK_SIZE)
                        if not chunk_data:
                            break
                        f.write(chunk_data)
            except Exception as e:
                raise ServiceError(
                    message="Failed to save chunk",
                    details={"error": str(e)},
                )

            # Update session metadata
            session_metadata["uploaded_chunks"].append(int(chunk_index))
            try:
                with open(os.path.join(session_dir, "session.json"), "w") as f:
                    json.dump(session_metadata, f, indent=2)
            except Exception as e:
                raise ServiceError(
                    message="Failed to update session metadata",
                    details={"error": str(e)},
                )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Chunk {chunk_index} uploaded successfully",
                },
            )
        except Exception as e:
            logger.error(f"Error uploading document chunk: {str(e)}")
            return handle_error(e)
        finally:
            await chunk.close()

    @router.post("/api/finalize-document-upload")
        """
    Create finalize document upload.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Parse request data
            body = await request.json()
            session_id = body.get("sessionId")

            if not session_id:
                raise HTTPException(status_code=400, detail="Session ID is required")

            # Validate session
            session_dir = os.path.join(DOCUMENT_STORAGE_PATH, f"temp_{session_id}")
            if not os.path.exists(session_dir):
                raise HTTPException(status_code=404, detail="Session not found")

            # Read session metadata
            with open(os.path.join(session_dir, "session.json"), "r") as f:
                session_metadata = json.load(f)

            # Create final document directory
            document_id = str(uuid.uuid4())
            document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
            os.makedirs(document_dir, exist_ok=True)

            # Combine chunks
            final_file_path = os.path.join(document_dir, session_metadata["file_name"])
            with open(final_file_path, "wb") as final_file:
                for chunk_index in range(session_metadata["total_chunks"]):
                    chunk_path = os.path.join(session_dir, f"chunk_{chunk_index}")
                    if not os.path.exists(chunk_path):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing chunk {chunk_index}",
                        )
                    with open(chunk_path, "rb") as chunk_file:
                        final_file.write(chunk_file.read())

            # Create document metadata
            metadata = {
                "id": document_id,
                "original_filename": session_metadata["file_name"],
                "file_path": final_file_path,
                "file_size": os.path.getsize(final_file_path),
                "file_type": os.path.splitext(session_metadata["file_name"])[1].lower(),
                "upload_timestamp": datetime.now().isoformat(),
                "processing_status": "ready",
            }

            # Save metadata
            with open(os.path.join(document_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

            # Clean up session directory
            shutil.rmtree(session_dir)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "document_id": document_id,
                    "message": "Document upload finalized successfully",
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error finalizing document upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error finalizing document upload: {str(e)}",
            )

    @router.post("/api/process-documents-with-pricing")
        """
    Create process documents with pricing.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
        try:
            # Extract document IDs and query from request
            document_ids = request.get("documentIds", [])
            query = request.get("query", "")

            if not document_ids:
                raise HTTPException(status_code=400, detail="No document IDs provided")

            # Process documents in background
            background_tasks.add_task(process_document_context, document_ids, query)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Document processing started",
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing documents: {str(e)}",
            )

    async def process_document_context(document_ids: List[str], query: str) -> str:
        """
        Process document context asynchronously.

        Args:
            document_ids: List of document IDs to process
            query: The query to process against the documents

        Returns:
            str: Processing result
        """
        try:
            # Process documents using the document processor
            result = document_processor.process_documents(
                document_data=[
                    {
                        "id": doc_id,
                        "path": os.path.join(
                            DOCUMENT_STORAGE_PATH, doc_id, "metadata.json"
                        ),
                    }
                    for doc_id in document_ids
                ]
            )
            return str(result)
        except Exception as e:
            logger.error(f"Error processing document context: {str(e)}")
            raise

    return router
