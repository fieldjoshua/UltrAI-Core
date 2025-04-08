import hashlib
import json
import logging
import mimetypes
import os
import random
import re
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)


# Cache implementation with both memory and disk options
class DocumentCache:
    """Document cache with both memory and disk options"""

    def __init__(self, cache_dir: str = ".cache", memory_size: int = 100):
        self.memory_cache = {}
        self.memory_size = memory_size
        self.cache_dir = cache_dir
        self.stats = {"hits": 0, "misses": 0}

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

    def _get_disk_path(self, key: str) -> str:
        """Get the path to the disk cache file for a key"""
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get an item from cache, first trying memory then disk"""
        # Check memory cache first
        if key in self.memory_cache:
            self.stats["hits"] += 1
            return self.memory_cache[key]

        # Check disk cache
        disk_path = self._get_disk_path(key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Also store in memory for faster access next time
                if len(self.memory_cache) < self.memory_size:
                    self.memory_cache[key] = data

                self.stats["hits"] += 1
                return data
            except Exception as e:
                logging.warning(f"Error reading from disk cache: {e}")

        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set an item in both memory and disk cache"""
        # Memory cache (LRU-like behavior by removing oldest entries if full)
        if len(self.memory_cache) >= self.memory_size:
            # Remove the first (oldest) item
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]

        # Add to memory cache
        self.memory_cache[key] = value

        # Disk cache
        disk_path = self._get_disk_path(key)
        try:
            with open(disk_path, "w", encoding="utf-8") as f:
                json.dump(value, f)
        except Exception as e:
            logging.warning(f"Error writing to disk cache: {e}")

    def clear(self) -> None:
        """Clear both memory and disk cache"""
        # Clear memory cache
        self.memory_cache = {}

        # Clear disk cache
        for file in os.listdir(self.cache_dir):
            if file.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                except Exception as e:
                    logging.warning(f"Error removing cache file {file}: {e}")


class UltraDocumentsOptimized:
    """
    Optimized document processing class for Ultra.
    This version is a simplified implementation that can process documents
    and extract content from them.
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        embedding_model: str = "default",
        max_workers: int = 4,
        memory_cache_size: int = 100,
    ):
        """
        Initialize the document processor.

        Args:
            cache_enabled: Whether to cache document processing results
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
            embedding_model: Model to use for embeddings (if available)
            max_workers: Maximum number of worker threads
            memory_cache_size: Maximum number of items in memory cache
        """
        self.cache_enabled = cache_enabled
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.max_workers = max_workers
        self.memory_cache_size = memory_cache_size

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"Initialized UltraDocumentsOptimized with chunk_size={chunk_size}"
        )

        # Initialize cache if enabled
        if cache_enabled:
            self.cache = DocumentCache(
                cache_dir=".cache", memory_size=memory_cache_size
            )
            self.logger.info("Document cache initialized")

        # Initialize the embedding engine if available
        try:
            from sentence_transformers import SentenceTransformer

            # Use a smaller, faster model for embedding
            self.embedding_engine = SentenceTransformer(embedding_model)
            self.logger.info(f"Document embedding model initialized: {embedding_model}")
            self.embeddings_available = True
        except Exception as e:
            self.logger.warning(f"Embeddings not available: {e}")
            self.embeddings_available = False

    def _generate_cache_key(self, file_path: str) -> str:
        """Generate a cache key for a file based on its path, size, and modification time"""
        # Get file metadata
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        file_mtime = file_stats.st_mtime

        # Combine into a unique string and hash it
        key_data = f"{file_path}|{file_size}|{file_mtime}|{self.chunk_size}|{self.chunk_overlap}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_file_extension(self, file_path: str) -> str:
        """Get the file extension from a path"""
        return os.path.splitext(file_path)[1].lower()

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type using mime library and extension"""
        ext = self._get_file_extension(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type:
            if mime_type.startswith("text/"):
                return "text"
            elif mime_type == "application/pdf":
                return "pdf"
            elif mime_type.startswith(
                "application/vnd.openxmlformats-officedocument.wordprocessingml"
            ):
                return "docx"
            elif mime_type.startswith("application/msword"):
                return "doc"

        # Fallback to extension-based detection
        ext_map = {
            ".txt": "text",
            ".md": "text",
            ".pdf": "pdf",
            ".docx": "docx",
            ".doc": "doc",
        }

        return ext_map.get(ext, "unknown")

    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks with smart splitting"""
        if not text:
            return []

        # Clean the text
        text = re.sub(r"\s+", " ", text).strip()

        # Split by proper paragraph boundaries first
        paragraphs = re.split(r"\n\s*\n", text)

        chunks = []
        current_chunk = ""
        current_length = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            paragraph_length = len(paragraph)

            # If this paragraph alone exceeds chunk size, we need to split it
            if paragraph_length > self.chunk_size:
                # If we have content in the current chunk, add it first
                if current_chunk:
                    chunks.append({"text": current_chunk, "length": current_length})
                    current_chunk = ""
                    current_length = 0

                # Split the long paragraph by sentences
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                sentence_chunk = ""
                sentence_length = 0

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    sentence_len = len(sentence)

                    # If adding this sentence would exceed the chunk size
                    if sentence_length + sentence_len + 1 > self.chunk_size:
                        # Add the current sentence chunk if it's not empty
                        if sentence_chunk:
                            chunks.append(
                                {"text": sentence_chunk, "length": sentence_length}
                            )

                        # If this single sentence is longer than chunk_size, we need to forcibly split it
                        if sentence_len > self.chunk_size:
                            words = sentence.split()
                            word_chunk = ""
                            word_length = 0

                            for word in words:
                                word_len = len(word)
                                if word_length + word_len + 1 > self.chunk_size:
                                    chunks.append(
                                        {"text": word_chunk, "length": word_length}
                                    )
                                    word_chunk = word
                                    word_length = word_len
                                else:
                                    if word_chunk:
                                        word_chunk += " " + word
                                        word_length += word_len + 1
                                    else:
                                        word_chunk = word
                                        word_length = word_len

                            if word_chunk:
                                chunks.append(
                                    {"text": word_chunk, "length": word_length}
                                )

                            sentence_chunk = ""
                            sentence_length = 0
                        else:
                            # Start a new sentence chunk with this sentence
                            sentence_chunk = sentence
                            sentence_length = sentence_len
                    else:
                        # Add to the current sentence chunk
                        if sentence_chunk:
                            sentence_chunk += " " + sentence
                            sentence_length += sentence_len + 1
                        else:
                            sentence_chunk = sentence
                            sentence_length = sentence_len

                # Add any remaining sentence chunk
                if sentence_chunk:
                    chunks.append({"text": sentence_chunk, "length": sentence_length})

            # If adding this paragraph would exceed the chunk size
            elif current_length + paragraph_length + 1 > self.chunk_size:
                # Add the current chunk and start a new one
                chunks.append({"text": current_chunk, "length": current_length})
                current_chunk = paragraph
                current_length = paragraph_length
            else:
                # Add to the current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                    current_length += paragraph_length + 2
                else:
                    current_chunk = paragraph
                    current_length = paragraph_length

        # Add the final chunk if there is one
        if current_chunk:
            chunks.append({"text": current_chunk, "length": current_length})

        # Add overlapping from previous chunks
        final_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0 and self.chunk_overlap > 0:
                prev_chunk = chunks[i - 1]
                # Add overlap from previous chunk if possible
                overlap_text = prev_chunk["text"]
                if len(overlap_text) > self.chunk_overlap:
                    overlap_text = overlap_text[-self.chunk_overlap :]
                    # Try to find sentence boundary
                    sentence_boundary = re.search(r"(?<=[.!?])\s+", overlap_text)
                    if sentence_boundary:
                        # Start from the beginning of the first sentence after the boundary
                        overlap_text = overlap_text[sentence_boundary.end() :]

                # Prepend the overlap to the current chunk
                if overlap_text:
                    chunk["text"] = overlap_text + "\n\n" + chunk["text"]

            # Add index and other metadata
            chunk["index"] = i
            chunk["page"] = None  # Add page info for PDFs if available

            final_chunks.append(chunk)

        # Add embeddings if available
        if self.embeddings_available:
            try:
                texts = [chunk["text"] for chunk in final_chunks]
                embeddings = self.embedding_engine.encode(texts)

                for i, embedding in enumerate(embeddings):
                    final_chunks[i]["embedding"] = embedding.tolist()
            except Exception as e:
                self.logger.warning(f"Error generating embeddings: {e}")

        # Calculate relevance scores (placeholder - will be replaced by actual relevance to query)
        for i, chunk in enumerate(final_chunks):
            # Just use a placeholder relevance score
            chunk["relevance"] = 0.9 - (
                i * 0.05
            )  # Slightly decreasing relevance for simplicity

        return final_chunks

    def _read_text_file(self, file_path: str) -> str:
        """Read a text file and return its content"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading text file {file_path}: {e}")
            return ""

    def _read_pdf_file(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Read a PDF file and return its content with page information"""
        content = ""
        pages_info = []

        try:
            # Try PyPDF2 first
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    if content:
                        content += "\n\n"
                    content += page_text
                    pages_info.append(
                        {"page": i + 1, "text": page_text, "offset": len(content)}
                    )

        except Exception as e:
            self.logger.warning(f"Error with PyPDF2 for {file_path}: {e}")

            # Fallback to PyMuPDF if available
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(file_path)
                for i, page in enumerate(doc):
                    page_text = page.get_text()
                    if page_text:
                        if content:
                            content += "\n\n"
                        content += page_text
                        pages_info.append(
                            {"page": i + 1, "text": page_text, "offset": len(content)}
                        )
                doc.close()

            except Exception as e2:
                self.logger.error(f"Failed to read PDF with PyMuPDF: {e2}")

        if not content:
            self.logger.warning(f"Could not extract text from PDF: {file_path}")

        return content, pages_info

    def _read_docx_file(self, file_path: str) -> str:
        """Read a DOCX file and return its content"""
        try:
            from docx import Document

            doc = Document(file_path)
            return "\n\n".join(
                [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
            )
        except Exception as e:
            self.logger.error(f"Error reading DOCX file {file_path}: {e}")
            return ""

    def _read_doc_file(self, file_path: str) -> str:
        """Read a DOC file and return its content using textract"""
        try:
            import textract

            return textract.process(file_path).decode("utf-8")
        except Exception as e:
            self.logger.error(f"Error reading DOC file {file_path}: {e}")
            return ""

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file and convert to chunks"""
        self.logger.info(f"Processing file: {file_path}")

        start_time = time.time()

        # Check if result is in cache
        if self.cache_enabled:
            cache_key = self._generate_cache_key(file_path)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.logger.info(f"Using cached result for {file_path}")
                return cached_result

        file_type = self._detect_file_type(file_path)
        content = ""
        pages_info = []

        # Extract content based on file type
        if file_type == "text":
            content = self._read_text_file(file_path)
        elif file_type == "pdf":
            content, pages_info = self._read_pdf_file(file_path)
        elif file_type == "docx":
            content = self._read_docx_file(file_path)
        elif file_type == "doc":
            content = self._read_doc_file(file_path)
        else:
            self.logger.warning(f"Unsupported file type: {file_type} for {file_path}")
            content = f"Unsupported file type: {file_type}"

        # Process the content into chunks
        chunks = self._chunk_text(content)

        # Add page information if available
        if pages_info:
            for chunk in chunks:
                # Find the page this chunk belongs to based on offset
                chunk_start = content.find(chunk["text"])
                if chunk_start >= 0:
                    for page_info in pages_info:
                        if chunk_start >= page_info["offset"]:
                            chunk["page"] = page_info["page"]
                        else:
                            break

        # Create the result
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": file_type,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "processed_at": time.time(),
            "processing_time": time.time() - start_time,
        }

        # Cache the result if enabled
        if self.cache_enabled:
            cache_key = self._generate_cache_key(file_path)
            self.cache.set(cache_key, result)

        return result

    def process_document(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Process a document (wrapper around process_file for backward compatibility)"""
        return self.process_file(file_path, **kwargs)

    def get_relevant_chunks(
        self, query: str, document_chunks: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Get the most relevant chunks for a query using embeddings if available"""
        if not document_chunks:
            return []

        # If we have embeddings available, use semantic search
        if self.embeddings_available:
            try:
                # Generate query embedding
                query_embedding = self.embedding_engine.encode(query).tolist()

                # Calculate similarity for each chunk
                for chunk in document_chunks:
                    # Skip chunks without embeddings
                    if "embedding" not in chunk:
                        chunk["relevance"] = 0
                        continue

                    # Calculate cosine similarity
                    dot_product = sum(
                        a * b for a, b in zip(query_embedding, chunk["embedding"])
                    )
                    magnitude1 = sum(a**2 for a in query_embedding) ** 0.5
                    magnitude2 = sum(b**2 for b in chunk["embedding"]) ** 0.5

                    if magnitude1 * magnitude2 == 0:
                        chunk["relevance"] = 0
                    else:
                        chunk["relevance"] = dot_product / (magnitude1 * magnitude2)

                # Sort by relevance and return top_k
                sorted_chunks = sorted(
                    document_chunks, key=lambda x: x.get("relevance", 0), reverse=True
                )
                return sorted_chunks[:top_k]

            except Exception as e:
                self.logger.warning(f"Error in semantic search: {e}")
                # Fall back to keyword search

        # Simple keyword-based relevance as fallback
        query_keywords = set(re.findall(r"\w+", query.lower()))

        for chunk in document_chunks:
            text = chunk.get("text", "").lower()
            text_keywords = set(re.findall(r"\w+", text))

            # Calculate simple keyword overlap score
            overlap = len(query_keywords.intersection(text_keywords))
            chunk["relevance"] = overlap / max(1, len(query_keywords))

        # Sort by relevance and return top_k
        sorted_chunks = sorted(
            document_chunks, key=lambda x: x.get("relevance", 0), reverse=True
        )
        return sorted_chunks[:top_k]

    def process_query(
        self, query: str, document_chunks: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Process a query against document chunks and return relevant context"""
        top_k = kwargs.get("top_k", 5)

        # Get the most relevant chunks
        relevant_chunks = self.get_relevant_chunks(query, document_chunks, top_k)

        # Extract the text from relevant chunks
        context = "\n\n".join([chunk.get("text", "") for chunk in relevant_chunks])

        return {"query": query, "relevant_chunks": relevant_chunks, "context": context}

    def cleanup(self):
        """Clean up resources"""
        # Clear the cache if enabled
        if self.cache_enabled:
            self.cache.clear()

        # Free up memory used by embedding model
        if self.embeddings_available:
            del self.embedding_engine
