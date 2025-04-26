import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

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
from sqlalchemy.orm import Session

from backend.config import Config
from backend.database import get_db
from backend.database.models import Document
from backend.services.document_processor import document_processor
from backend.utils.error_handler import handle_error

# Create a document router
document_router = APIRouter(prefix="/api", tags=["Documents"])

# Configure logging
logger = logging.getLogger("document_routes")

# Set document storage path from config
DOCUMENT_STORAGE_PATH = Config.DOCUMENT_STORAGE_PATH

# Define dependencies
db_dependency = Depends(get_db)
file_dependency = File(...)
form_dependency = Form(...)


@document_router.post("/documents/upload")
async def upload_document(
    file: UploadFile = file_dependency,
    db: Session = db_dependency,
):
    """Upload a document for processing."""
    try:
        # Validate file extension
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No filename provided")

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {Config.ALLOWED_EXTENSIONS}",
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = os.path.join(DOCUMENT_STORAGE_PATH, f"{file_id}{file_ext}")

        # Ensure storage directory exists
        os.makedirs(DOCUMENT_STORAGE_PATH, exist_ok=True)

        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Create document record
        document = Document(
            id=file_id,
            filename=file.filename,
            status="uploaded",
            user_id="test_user",  # TODO: Get from auth
            file_path=str(file_path),
            uploaded_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status,
            "uploaded_at": document.uploaded_at,
        }

    except Exception as e:
        handle_error(e)


@document_router.get("/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: Session = db_dependency,
):
    """Get document processing status."""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "document_id": document.id,
            "status": document.status,
            "processing_progress": document.processing_progress,
        }

    except Exception as e:
        handle_error(e)


@document_router.get("/api/documents", response_model=List[Dict[str, Any]])
async def list_documents(
    db: Session = db_dependency,
):
    """List all documents."""
    try:
        documents = db.query(Document).all()
        return [
            {
                "document_id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "uploaded_at": doc.uploaded_at,
            }
            for doc in documents
        ]

    except Exception as e:
        handle_error(e)


@document_router.post("/api/create-document-session")
async def create_document_session(request: Request):
    """Create a session for chunked document upload"""
    try:
        # Parse request data
        body = await request.json()
        file_name = body.get("fileName", "")
        file_size = body.get("fileSize", 0)
        chunk_size = body.get("chunkSize", 1024 * 1024)
        total_chunks = body.get("totalChunks", 0)

        # Validate inputs
        if not all([file_name, file_size, chunk_size, total_chunks]):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Missing required parameters"},
            )

        # Create a session ID
        session_id = str(uuid.uuid4())

        # Create session directory
        session_dir = os.path.join("temp_uploads", session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Create session metadata
        metadata = {
            "session_id": session_id,
            "file_name": file_name,
            "file_size": file_size,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "received_chunks": 0,
            "created_at": datetime.now().isoformat(),
        }

        # Save metadata
        with open(os.path.join(session_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f)

        return JSONResponse(
            content={
                "success": True,
                "sessionId": session_id,
                "message": "Upload session created",
            }
        )
    except Exception as e:
        logger.error(f"Error creating document session: {str(e)}")
        return JSONResponse(
            status_code=500, content={"success": False, "message": f"Error: {str(e)}"}
        )


@document_router.post("/api/upload-document-chunk")
async def upload_document_chunk(
    sessionId: str = form_dependency("sessionId"),
    chunkIndex: str = form_dependency("chunkIndex"),
    chunk: UploadFile = file_dependency,
):
    """Upload a chunk of a document in a chunked upload session"""
    try:
        # Verify session exists
        session_dir = os.path.join("temp_uploads", sessionId)
        if not os.path.exists(session_dir):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Session not found"},
            )

        # Verify metadata exists
        metadata_path = os.path.join(session_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Session metadata not found"},
            )

        # Load metadata
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Save the chunk
        chunk_index = int(chunkIndex)
        chunk_path = os.path.join(session_dir, f"chunk_{chunk_index}")

        # Write chunk to file
        with open(chunk_path, "wb") as f:
            chunk_content = await chunk.read()
            f.write(chunk_content)

        # Update metadata
        metadata["received_chunks"] = metadata.get("received_chunks", 0) + 1
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        return JSONResponse(
            content={
                "success": True,
                "message": f"Chunk {chunk_index} received",
                "received": metadata["received_chunks"],
                "total": metadata["total_chunks"],
            }
        )
    except Exception as e:
        logger.error(f"Error uploading chunk: {str(e)}")
        return JSONResponse(
            status_code=500, content={"success": False, "message": f"Error: {str(e)}"}
        )
    finally:
        await chunk.close()


@document_router.post("/api/finalize-document-upload")
async def finalize_document_upload(request: Request):
    """Finalize a chunked document upload by combining all chunks"""
    try:
        # Parse request data
        body = await request.json()
        session_id = body.get("sessionId")
        file_name = body.get("fileName")

        # Validate inputs
        if not all([session_id, file_name]):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Missing required parameters"},
            )

        # Verify session exists
        session_dir = os.path.join("temp_uploads", session_id)
        if not os.path.exists(session_dir):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Session not found"},
            )

        # Load metadata
        metadata_path = os.path.join(session_dir, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Verify all chunks received
        received_chunks = metadata.get("received_chunks", 0)
        total_chunks = metadata.get("total_chunks", 0)

        if received_chunks != total_chunks:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Not all chunks received ({received_chunks}/{total_chunks})",
                },
            )

        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())

        # Create document storage path with the UUID
        document_dir = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
        os.makedirs(document_dir, exist_ok=True)

        # Combine all chunks into the final file
        file_path = os.path.join(document_dir, file_name)
        with open(file_path, "wb") as outfile:
            for i in range(total_chunks):
                chunk_path = os.path.join(session_dir, f"chunk_{i}")
                if os.path.exists(chunk_path):
                    with open(chunk_path, "rb") as chunk_file:
                        outfile.write(chunk_file.read())

        # Get file size
        file_size = os.path.getsize(file_path)

        # Create document metadata
        doc_metadata = {
            "id": document_id,
            "original_filename": file_name,
            "file_path": file_path,
            "file_size": file_size,
            "file_type": os.path.splitext(file_name)[1].lower(),
            "upload_timestamp": datetime.now().isoformat(),
            "processing_status": "ready",
            "chunked_upload": True,
            "upload_session_id": session_id,
        }

        # Save document metadata
        with open(os.path.join(document_dir, "metadata.json"), "w") as f:
            json.dump(doc_metadata, f, indent=2)

        # Clean up the session directory
        try:
            shutil.rmtree(session_dir)
        except Exception as e:
            logger.warning(f"Could not clean up session directory: {str(e)}")

        return JSONResponse(
            content={
                "success": True,
                "message": "Document upload completed successfully",
                "id": document_id,
                "name": file_name,
                "size": file_size,
                "type": os.path.splitext(file_name)[1].lower(),
                "status": "uploaded",
            }
        )
    except Exception as e:
        logger.error(f"Error finalizing document upload: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error finalizing document upload: {str(e)}"
        )


# Use a dependency for processing document request
def get_document_request(request: Dict[str, Any] = Depends()):
    """Dependency to validate document processing request"""
    return request


@document_router.post("/api/process-documents-with-pricing")
async def process_documents_with_pricing(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any] = Depends(get_document_request),
):
    """Process documents with pricing integration"""
    try:
        # Extract parameters from request
        document_ids = request.get("documentIds", [])
        query = request.get("query", "")
        # user_id available but not used in this function
        # user_id = request.get("userId")

        if not document_ids or not query:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        # Process documents in the background
        background_tasks.add_task(process_document_context, document_ids, query)

        return {
            "status": "processing",
            "message": f"Processing {len(document_ids)} documents with query: {query[:30]}...",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing documents: {str(e)}"
        )


async def process_document_context(document_ids: List[str], query: str) -> str:
    """Process documents and extract context relevant to the query"""
    try:
        # Gather document data for processing
        document_data = []

        for doc_id in document_ids:
            doc_dir = os.path.join(DOCUMENT_STORAGE_PATH, doc_id)
            if not os.path.exists(doc_dir):
                logger.warning(f"Document directory not found: {doc_id}")
                continue

            # Get metadata
            metadata_path = os.path.join(doc_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                logger.warning(f"Document metadata not found: {doc_id}")
                continue

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            document_data.append(
                {
                    "id": doc_id,
                    "path": metadata.get("file_path"),
                    "name": metadata.get("original_filename"),
                    "type": metadata.get("file_type"),
                }
            )

        # Process documents with the document processor
        if document_data:
            result = document_processor.process_documents(document_data)
            logger.info(
                f"Processed {result.get('chunks_processed', 0)} chunks from {len(document_data)} documents"
            )
            return f"Processed {result.get('chunks_processed', 0)} chunks"
        else:
            logger.warning("No valid documents found for processing")
            return "No valid documents found"
    except Exception as e:
        logger.error(f"Error in document processing: {str(e)}")
        return f"Error in document processing: {str(e)}"
