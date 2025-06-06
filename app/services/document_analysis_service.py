"""
Document Analysis Service

This service handles document analysis logic, processing documents and generating analysis results.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

from app.config import Config
from app.services.document_processor import document_processor
from app.services.llm_config_service import llm_config_service
from app.services.prompt_service import PromptService

# Configure logging
logger = logging.getLogger("document_analysis_service")


class DocumentAnalysisService:
    """Service for document analysis operations"""

    def __init__(self, prompt_service: Optional[PromptService] = None):
        """Initialize document analysis service"""
        self.prompt_service = prompt_service or PromptService(
            llm_config_service=llm_config_service
        )
        self.document_processor = document_processor

    async def analyze_document(
        self,
        document_id: str,
        models: List[str],
        ultra_model: str,
        pattern: str = "comprehensive_analysis",
        options: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a document using specified models

        Args:
            document_id: ID of the document to analyze
            models: List of LLM models to use
            ultra_model: Ultra model to use for final analysis
            pattern: Analysis pattern to use
            options: Additional options for analysis

        Returns:
            Document analysis results
        """
        # Start timer
        start_time = time.time()

        try:
            # Get document from storage
            document_path = os.path.join(Config.DOCUMENT_STORAGE_PATH, document_id)
            if not os.path.exists(document_path):
                raise ValueError(f"Document not found: {document_id}")

            # Read document metadata
            metadata_path = os.path.join(document_path, "metadata.json")
            if not os.path.exists(metadata_path):
                raise ValueError(f"Document metadata not found: {document_id}")

            import json

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Get file path
            file_path = metadata.get("file_path")
            if not file_path or not os.path.exists(file_path):
                raise ValueError(f"Document file not found: {file_path}")

            # Process document to extract content
            document_data = [
                {
                    "id": document_id,
                    "path": file_path,
                    "name": metadata.get("original_filename", ""),
                    "type": metadata.get("file_type", ""),
                }
            ]

            # Use document processor to extract content
            processing_result = self.document_processor.process_documents(document_data)
            document_chunks = processing_result.get("chunks", [])

            if not document_chunks:
                raise ValueError("No content could be extracted from document")

            # Combine chunks for analysis
            document_content = "\n\n".join(
                [chunk.get("text", "") for chunk in document_chunks]
            )

            # Create analysis prompt
            analysis_prompt = (
                f"The following is the content of a document that requires analysis. "
                f"Please analyze this content according to the specified pattern.\n\n"
                f"Document Content:\n{document_content}"
            )

            # Process the analysis
            result = await self.prompt_service.analyze_prompt(
                prompt=analysis_prompt,
                models=models,
                ultra_model=ultra_model,
                pattern=pattern,
                options=options or {},
            )

            # Add document metadata
            result["document_metadata"] = {
                "id": document_id,
                "name": metadata.get("original_filename", ""),
                "type": metadata.get("file_type", ""),
                "size": metadata.get("file_size", 0),
            }

            # Calculate processing time
            processing_time = time.time() - start_time
            result["performance"]["total_processing_time"] = processing_time

            return result

        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise


# Create singleton instance
document_analysis_service = DocumentAnalysisService()
