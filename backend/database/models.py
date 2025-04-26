from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    # Relationships
    analyses = relationship("Analysis", back_populates="document")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    llm_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="analyses")
