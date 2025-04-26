import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from fastapi import HTTPException
from openai import AsyncOpenAI


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def process_document(
        self, document_id: str, llm_id: str, analysis_type: str, prompt: str
    ) -> Dict[str, Any]:
        """Process a document with the specified LLM."""
        pass


class MockLLMService(LLMService):
    """Mock LLM service for testing and development."""

    async def process_document(
        self, document_id: str, llm_id: str, analysis_type: str, prompt: str
    ) -> Dict[str, Any]:
        """Process a document with a mock LLM."""
        # Simulate processing delay
        await asyncio.sleep(1)

        # Return mock response
        return {
            "analysis_id": str(uuid4()),
            "status": "completed",
            "result": f"Mock analysis result for {analysis_type} using {llm_id}",
            "created_at": datetime.utcnow().isoformat(),
        }


class OpenAIService(LLMService):
    """OpenAI API integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)

    async def process_document(
        self, document_id: str, llm_id: str, analysis_type: str, prompt: str
    ) -> Dict[str, Any]:
        """Process a document using OpenAI's API."""
        try:
            # Get document content
            document_content = await self._get_document_content(document_id)

            # Prepare prompt
            full_prompt = f"{prompt}\n\nDocument content:\n{document_content}"

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=llm_id,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": full_prompt},
                ],
            )

            return {
                "analysis_id": str(uuid4()),
                "status": "completed",
                "result": response.choices[0].message.content,
                "created_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document with OpenAI: {str(e)}",
            )

    async def _get_document_content(self, document_id: str) -> str:
        """Get document content from storage."""
        # TODO: Implement document content retrieval
        return "Mock document content"
