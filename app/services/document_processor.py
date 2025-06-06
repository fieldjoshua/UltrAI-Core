import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger("document_processor")


class UltraDocumentsOptimized:
    """Document processor service for handling document processing and chunking"""

    def __init__(self):
        """Initialize the optimized document processor"""
        self.cache_enabled = True

        from backend.utils.cache import CacheObject

        self.cache = CacheObject()

    def process_document(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Process a document and extract text chunks with mock relevance"""
        try:
            # For demonstration, just return some mock chunks
            chunks = []

            # Handle different file types - safely handle None
            if file_path:
                extension = os.path.splitext(file_path)[1].lower()
            else:
                extension = ""

            # For text files, try to read content
            if file_path and extension in [".txt", ".md"]:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Split into chunks (simplified)
                    lines = content.split("\n")
                    chunk_size = 10  # lines per chunk
                    for i in range(0, len(lines), chunk_size):
                        chunk_text = "\n".join(lines[i : i + chunk_size])
                        if chunk_text.strip():
                            chunks.append(
                                {"text": chunk_text, "relevance": 0.8}  # Mock relevance
                            )
                except Exception as e:
                    logger.error(f"Error reading text file: {str(e)}")
                    # Fall back to mock chunks
                    chunks = [
                        {"text": f"Mock content from {file_path}", "relevance": 0.7}
                    ]
            else:
                # For other file types, return mock chunks
                chunks = [
                    {
                        "text": f"Mock content from {file_path or 'unknown'} - part 1",
                        "relevance": 0.8,
                    },
                    {
                        "text": f"Mock content from {file_path or 'unknown'} - part 2",
                        "relevance": 0.6,
                    },
                ]

            return {"chunks": chunks}
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {"chunks": [{"text": "Error processing document", "relevance": 0.1}]}

    def process_documents(self, document_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple documents"""
        total_chunks = 0
        processed_chunks = []

        for doc in document_data:
            path = doc.get("path", "")
            doc_result = self.process_document(path)
            doc_chunks = doc_result.get("chunks", [])
            total_chunks += len(doc_chunks)
            processed_chunks.extend(doc_chunks)

        return {"chunks_processed": total_chunks, "chunks": processed_chunks}


# Singleton instance of the document processor
document_processor = UltraDocumentsOptimized()
