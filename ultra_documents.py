from typing import Dict, Any, Optional, List, Union
import os
import PyPDF2
import io
from pathlib import Path
from ultra_base import UltraBase
import logging

class UltraDocuments(UltraBase):
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[Any] = None,
        rate_limits: Optional[Any] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None
    ):
        super().__init__(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features
        )
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.txt': self._process_text,
            '.md': self._process_text,
            '.docx': self._process_docx,
            '.doc': self._process_doc
        }
    
    def _process_pdf(self, file_path: Union[str, Path]) -> str:
        """Extract text from a PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"Error processing PDF file {file_path}: {str(e)}")
            raise
    
    def _process_text(self, file_path: Union[str, Path]) -> str:
        """Extract text from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise
    
    def _process_docx(self, file_path: Union[str, Path]) -> str:
        """Extract text from a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            self.logger.error(f"Error processing DOCX file {file_path}: {str(e)}")
            raise
    
    def _process_doc(self, file_path: Union[str, Path]) -> str:
        """Extract text from a DOC file."""
        try:
            import textract
            return textract.process(file_path).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error processing DOC file {file_path}: {str(e)}")
            raise
    
    def process_document(self, file_path: Union[str, Path]) -> str:
        """Process a document and extract its text content."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        return self.supported_formats[file_extension](file_path)
    
    def process_documents(self, file_paths: List[Union[str, Path]]) -> Dict[str, str]:
        """Process multiple documents and return their text content."""
        results = {}
        for file_path in file_paths:
            try:
                results[str(file_path)] = self.process_document(file_path)
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {str(e)}")
                results[str(file_path)] = f"Error: {str(e)}"
        return results 