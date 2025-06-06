from typing import List, Optional

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    """Model representing a chunk of text from a document with relevance score"""

    text: str
    relevance: float
    page: Optional[int] = None


class ProcessedDocument(BaseModel):
    """Model representing a processed document with its chunks"""

    id: str
    name: str
    chunks: List[DocumentChunk]
    totalChunks: int
    type: str


class DocumentUploadResponse(BaseModel):
    """Response model for document upload operations"""

    id: str
    name: str
    size: int
    type: str
    status: str
    message: str
