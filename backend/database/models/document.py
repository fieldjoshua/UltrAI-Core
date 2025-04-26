"""
Document models for the Ultra backend.

This module defines the SQLAlchemy ORM models for documents and document chunks.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class DocumentStatus(enum.Enum):
    """Document processing status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(enum.Enum):
    """Document type enumeration"""

    PDF = "pdf"
    TXT = "txt"
    MD = "md"
    DOC = "doc"
    DOCX = "docx"
    UNKNOWN = "unknown"


class Document(Base):
    """Document model for storing metadata about uploaded documents"""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Document metadata
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(Enum(DocumentType), default=DocumentType.UNKNOWN, nullable=False)
    mime_type = Column(String, nullable=True)

    # Processing status
    status = Column(
        Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False
    )
    error_message = Column(Text, nullable=True)

    # Processing metadata
    word_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    embedding_model = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    analyses = relationship("Analysis", back_populates="document")

    def __repr__(self) -> str:
        return f"<Document {self.filename} ({self.uuid})>"


class DocumentChunk(Base):
    """Document chunk model for storing parts of a document with embeddings"""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Chunk content
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)

    # Embedding data
    embedding = Column(JSONB, nullable=True)  # Storing vector as JSON
    embedding_model = Column(String, nullable=True)

    # Page info for PDFs and similar formats
    page_number = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.document_id}:{self.chunk_index}>"
