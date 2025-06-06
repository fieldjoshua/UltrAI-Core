"""
Document management routes for the Ultra backend.

This module provides endpoints for uploading, managing, and processing documents.
"""

import json
import logging
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
from fastapi.responses import JSONResponse

from app.models.document import DocumentUploadResponse
from app.services.document_processor import UltraDocumentsOptimized

# Configure logging
logger = logging.getLogger("document_routes")

# Set document storage path from config
DOCUMENT_STORAGE_PATH = os.getenv("DOCUMENT_STORAGE_PATH", "documents")

# Default values for document processing
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB chunks

# Default values for FastAPI dependencies
DEFAULT_FILE = File(...)
DEFAULT_FORM = Form(...)
DEFAULT_DEPENDS = Depends()


def create_router(document_processor: UltraDocumentsOptimized) -> APIRouter:
    """
    Create the document router with dependencies.

    Args:
        document_processor: The document processor instance to use for document operations

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Documents"])

    @router.post("/api/upload-document", response_model=DocumentUploadResponse)
    async def upload_document(file: UploadFile = DEFAULT_FILE):
        """Upload a document"""
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

            # Save the file
            with open(file_path, "wb") as f:
                # Read chunks to handle large files
                while True:
                    chunk = await file.read(DEFAULT_CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)

            # Get file size
            file_size = os.path.getsize(file_path)

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

            # Save metadata
            with open(os.path.join(document_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

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
            raise HTTPException(
                status_code=500, detail=f"Error uploading document: {str(e)}"
            )
        finally:
            await file.close()

    @router.get("/api/documents/{document_id}", response_model=Dict[str, Any])
    async def get_document(document_id: str):
        """Get document details by ID"""
        try:
            # Check if document directory exists
            document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
            if not os.path.exists(document_dir):
                raise HTTPException(status_code=404, detail="Document not found")

            # Check if metadata file exists
            metadata_path = os.path.join(document_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                raise HTTPException(
                    status_code=500, detail="Document metadata not found"
                )

            # Read metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            return {
                "id": metadata["id"],
                "name": metadata.get("original_filename", "Unknown"),
                "size": metadata.get("file_size", 0),
                "type": metadata.get("file_type", ""),
                "status": metadata.get("processing_status", "unknown"),
                "uploadDate": metadata.get("upload_timestamp", ""),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error getting document: {str(e)}"
            )

    @router.get("/api/documents", response_model=List[Dict[str, Any]])
    async def list_documents():
        """List all uploaded documents"""
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

                # Read metadata
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

            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error listing documents: {str(e)}"
            )

    @router.post("/api/create-document-session")
    async def create_document_session(request: Request):
        """Create a session for chunked document upload"""
        try:
            # Parse request data
            body = await request.json()
            file_name = body.get("fileName", "")
            file_size = body.get("fileSize", 0)
            chunk_size = body.get("chunkSize", DEFAULT_CHUNK_SIZE)
            total_chunks = body.get("totalChunks", 0)

            # Validate inputs
            if not all([file_name, file_size, chunk_size, total_chunks]):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "Missing required parameters",
                    },
                )

            # Create a unique session ID
            session_id = str(uuid.uuid4())

            # Create a temporary directory for the session
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

            with open(os.path.join(session_dir, "session.json"), "w") as f:
                json.dump(session_metadata, f, indent=2)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "sessionId": session_id,
                    "message": "Upload session created successfully",
                },
            )
        except Exception as e:
            logger.error(f"Error creating document session: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error creating session: {str(e)}",
                },
            )

    @router.post("/api/upload-document-chunk")
    async def upload_document_chunk(
        sessionId: str = DEFAULT_FORM,
        chunkIndex: str = DEFAULT_FORM,
        chunk: UploadFile = DEFAULT_FILE,
    ):
        """Upload a chunk of a document"""
        try:
            # Validate session
            session_dir = os.path.join(DOCUMENT_STORAGE_PATH, f"temp_{sessionId}")
            if not os.path.exists(session_dir):
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "Upload session not found"},
                )

            # Read session metadata
            with open(os.path.join(session_dir, "session.json"), "r") as f:
                session_metadata = json.load(f)

            # Validate chunk index
            chunk_index = int(chunkIndex)
            if chunk_index >= session_metadata["total_chunks"]:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "Invalid chunk index"},
                )

            # Save chunk
            chunk_path = os.path.join(session_dir, f"chunk_{chunk_index}")
            with open(chunk_path, "wb") as f:
                content = await chunk.read()
                f.write(content)

            # Update session metadata
            session_metadata["uploaded_chunks"].append(chunk_index)
            with open(os.path.join(session_dir, "session.json"), "w") as f:
                json.dump(session_metadata, f, indent=2)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Chunk {chunk_index} uploaded successfully",
                },
            )
        except Exception as e:
            logger.error(f"Error uploading document chunk: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error uploading chunk: {str(e)}",
                },
            )
        finally:
            await chunk.close()

    @router.post("/api/finalize-document-upload")
    async def finalize_document_upload(request: Request):
        """Finalize a chunked document upload"""
        try:
            # Parse request data
            body = await request.json()
            session_id = body.get("sessionId")

            if not session_id:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "Missing session ID"},
                )

            # Validate session
            session_dir = os.path.join(DOCUMENT_STORAGE_PATH, f"temp_{session_id}")
            if not os.path.exists(session_dir):
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "Upload session not found"},
                )

            # Read session metadata
            with open(os.path.join(session_dir, "session.json"), "r") as f:
                session_metadata = json.load(f)

            # Validate all chunks are uploaded
            if (
                len(session_metadata["uploaded_chunks"])
                != session_metadata["total_chunks"]
            ):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "Not all chunks have been uploaded",
                    },
                )

            # Create final document directory
            document_id = str(uuid.uuid4())
            document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
            os.makedirs(document_dir, exist_ok=True)

            # Combine chunks into final file
            final_file_path = os.path.join(document_dir, session_metadata["file_name"])
            with open(final_file_path, "wb") as outfile:
                for i in range(session_metadata["total_chunks"]):
                    chunk_path = os.path.join(session_dir, f"chunk_{i}")
                    with open(chunk_path, "rb") as infile:
                        outfile.write(infile.read())

            # Create document metadata
            document_metadata = {
                "id": document_id,
                "original_filename": session_metadata["file_name"],
                "file_path": final_file_path,
                "file_size": os.path.getsize(final_file_path),
                "file_type": os.path.splitext(session_metadata["file_name"])[1].lower(),
                "upload_timestamp": datetime.now().isoformat(),
                "processing_status": "ready",
            }

            # Save document metadata
            with open(os.path.join(document_dir, "metadata.json"), "w") as f:
                json.dump(document_metadata, f, indent=2)

            # Clean up temporary session directory
            shutil.rmtree(session_dir)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "documentId": document_id,
                    "message": "Document upload finalized successfully",
                },
            )
        except Exception as e:
            logger.error(f"Error finalizing document upload: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error finalizing upload: {str(e)}",
                },
            )

    def get_document_request(request: Dict[str, Any] = DEFAULT_DEPENDS):
        """Dependency for document processing request"""
        return request

    @router.post("/api/process-documents-with-pricing")
    async def process_documents_with_pricing(
        background_tasks: BackgroundTasks,
        request: Dict[str, Any] = DEFAULT_DEPENDS,
    ):
        """Process documents with pricing information"""
        try:
            # Extract document IDs and query from request
            document_ids = request.get("documentIds", [])
            query = request.get("query", "")

            if not document_ids or not query:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": "Missing document IDs or query",
                    },
                )

            # Process documents in background
            background_tasks.add_task(
                document_processor.process_documents,
                document_data=[{"id": doc_id} for doc_id in document_ids],
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Document processing started",
                },
            )
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error processing documents: {str(e)}",
                },
            )

    async def process_document_context(document_ids: List[str], query: str) -> str:
        """Process document context for a query"""
        try:
            # Process documents using document processor
            result = document_processor.process_documents(
                document_data=[{"id": doc_id} for doc_id in document_ids],
            )
            return str(result)
        except Exception as e:
            logger.error(f"Error processing document context: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document context: {str(e)}",
            )

    return router
