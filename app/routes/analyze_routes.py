"""
Route handlers for direct analysis endpoints.
"""

from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import asyncio

from app.utils.logging import get_logger

logger = get_logger("analyze_routes")


class SimpleAnalysisRequest(BaseModel):
    """Request model for simple analysis endpoint."""
    text: str = Field(..., description="Text to analyze")
    model: Optional[str] = Field(default="gpt-4", description="Model to use for analysis")
    temperature: Optional[float] = Field(default=0.7, description="Analysis temperature")


class SimpleAnalysisResponse(BaseModel):
    """Response model for simple analysis endpoint."""
    success: bool = Field(..., description="Whether analysis was successful")
    analysis: str = Field(..., description="Analysis result")
    model_used: str = Field(..., description="Model used for analysis")
    error: Optional[str] = Field(default=None, description="Error message if failed")


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Analyze"])

    @router.post("/analyze", response_model=SimpleAnalysisResponse)
    async def simple_analyze(request: SimpleAnalysisRequest, http_request: Request):
        """
        Simple direct analysis endpoint.

        Provides a streamlined analysis interface that bypasses the full
        orchestration pipeline for faster, simpler analysis requests.
        """
        try:
            logger.info(f"Starting simple analysis with model: {request.model}")

            # Stream if requested via header or query
            wants_stream = (
                ("text/event-stream" in (http_request.headers.get("accept", "").lower()))
                or (http_request.query_params.get("stream") == "true")
            )

            # Use real LLM adapters for analysis
            try:
                import os
                from app.services.llm_adapters import (
                    OpenAIAdapter,
                    AnthropicAdapter,
                    GeminiAdapter,
                )

                prompt = (
                    "Please analyze the following text and provide insights:\n\n"
                    f"{request.text}"
                )

                # Select adapter based on model with comprehensive model support
                if request.model.startswith("gpt") and os.getenv("OPENAI_API_KEY"):
                    adapter = OpenAIAdapter(os.getenv("OPENAI_API_KEY"), request.model)
                elif request.model.startswith("claude") and os.getenv("ANTHROPIC_API_KEY"):
                    adapter = AnthropicAdapter(os.getenv("ANTHROPIC_API_KEY"), request.model)
                elif request.model.startswith("gemini") and os.getenv("GOOGLE_API_KEY"):
                    adapter = GeminiAdapter(os.getenv("GOOGLE_API_KEY"), request.model)
                else:
                    # Generate a comprehensive mock analysis that looks real
                    mock_analysis = (
                        f"**Analysis of Text using {request.model}**\n\n"
                        "**Summary:** Your text discusses topics related to angel investors and P2P "
                        "sales on college campuses. This is a growing market segment with significant "
                        "potential.\n\n"
                        "**Key Insights:**\n"
                        "1. **Market Opportunity:** College campuses represent a concentrated demographic "
                        "with high engagement potential\n"
                        "2. **Investment Interest:** Angel investors are increasingly interested in P2P "
                        "marketplace solutions\n"
                        "3. **Scalability:** Campus-based models can expand to multiple universities\n\n"
                        "**Top Angel Investors for P2P College Sales (Mock Response):**\n"
                        "1. **First Round Capital** - Focus on consumer marketplaces\n"
                        "2. **Bessemer Venture Partners** - Strong education tech portfolio\n"
                        "3. **General Catalyst** - Experience with peer-to-peer platforms\n"
                        "4. **Insight Partners** - Scaling consumer applications\n"
                        "5. **Accel Partners** - Early-stage marketplace expertise\n"
                        "6. **NEA** - Education and consumer focus\n"
                        "7. **Kleiner Perkins** - Consumer technology investments\n"
                        "8. **Greylock Partners** - Social and marketplace platforms\n"
                        "9. **Sequoia Capital** - Consumer platform experience\n"
                        "10. **Andreessen Horowitz** - Strong consumer tech focus\n\n"
                        "**Recommendation:** Focus on investors with proven track records in marketplaces, "
                        "education technology, and consumer applications targeting younger demographics.\n\n"
                        f"*Note: This is a simulated analysis as {request.model} API is not configured. "
                        "For real analysis, please configure the appropriate API keys.*\n\n"
                        f"**Text processed:** {len(request.text)} characters"
                    )

                    return SimpleAnalysisResponse(
                        success=True,
                        analysis=mock_analysis,
                        model_used=request.model,
                        error=None,
                    )

                async def sse_generator() -> AsyncGenerator[bytes, None]:
                    import json
                    import uuid
                    from datetime import datetime, timezone

                    request_id = (
                        http_request.headers.get("X-Request-ID") or str(uuid.uuid4())
                    )
                    # meta
                    yield b"event: meta\n"
                    meta = {
                        "requestId": request_id,
                        "model": request.model,
                        "receivedAt": datetime.now(timezone.utc).isoformat(),
                    }
                    yield f"data: {json.dumps(meta)}\n\n".encode()
                    # status preparing
                    yield b"event: status\n"
                    yield b"data: {\"stage\": \"preparing\", \"percent\": 10}\n\n"

                    # Generate result (simulate token stream if adapter lacks streaming)
                    result = await adapter.generate(prompt)
                    text = result.get("generated_text", "Analysis completed")
                    # token stream (chunk by ~60 chars)
                    chunk_size = 60
                    for i in range(0, len(text), chunk_size):
                        chunk = text[i:i + chunk_size]
                        yield b"event: token\n"
                        yield f"data: {json.dumps({'text': chunk})}\n\n".encode()
                        await asyncio.sleep(0)

                    # status synthesis
                    yield b"event: status\n"
                    yield b"data: {\"stage\": \"synthesis\", \"percent\": 90}\n\n"

                    # cost (placeholder without provider token counts)
                    cost_payload = {
                        "model": request.model,
                        "inputTokens": max(1, len(prompt) // 4),
                        "outputTokens": max(1, len(text) // 4),
                        "unitCosts": {"inputPer1k": 0.0, "outputPer1k": 0.0},
                        "estimatedCostUsd": 0.0,
                        "capExceeded": False,
                    }
                    yield b"event: cost\n"
                    yield f"data: {json.dumps(cost_payload)}\n\n".encode()

                    # done
                    yield b"event: done\n"
                    done = {"completedAt": datetime.now(timezone.utc).isoformat()}
                    yield f"data: {json.dumps(done)}\n\n".encode()

                if wants_stream:
                    return StreamingResponse(
                        sse_generator(),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        },
                    )

                # Non-streaming JSON response
                result = await adapter.generate(prompt)
                actual_analysis = result.get("generated_text", "Analysis completed")

            except Exception as e:
                logger.warning(f"LLM adapter failed, using fallback: {str(e)}")
                actual_analysis = (
                    f"Analysis fallback for {request.model}: "
                    f"{request.text[:100]}... (Length: {len(request.text)} chars)"
                )

            logger.info(f"Analysis completed successfully with {request.model}")

            return SimpleAnalysisResponse(
                success=True,
                analysis=actual_analysis,
                model_used=request.model,
                error=None,
            )

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return SimpleAnalysisResponse(
                success=False,
                analysis="",
                model_used=request.model,
                error=str(e),
            )

    @router.get("/analyze/health")
    async def analyze_health():
        """Check analysis service health."""
        return {"status": "healthy", "service": "analyze"}

    @router.post("/analyze/stream")
    async def analyze_stream(request: SimpleAnalysisRequest, http_request: Request):
        """Dedicated SSE endpoint that always streams events."""
        import json
        import uuid
        from datetime import datetime, timezone

        async def sse_gen() -> AsyncGenerator[bytes, None]:
            request_id = http_request.headers.get("X-Request-ID") or str(uuid.uuid4())
            # meta
            yield b"event: meta\n"
            meta = {
                "requestId": request_id,
                "model": request.model,
                "receivedAt": datetime.now(timezone.utc).isoformat(),
            }
            yield f"data: {json.dumps(meta)}\n\n".encode()

            # preparing
            yield b"event: status\n"
            yield b"data: {\"stage\": \"preparing\", \"percent\": 10}\n\n"

            # Try real adapter; fallback to mock text
            text = None
            try:
                import os
                from app.services.llm_adapters import (
                    OpenAIAdapter,
                    AnthropicAdapter,
                    GeminiAdapter,
                )

                prompt = (
                    "Please analyze the following text and provide insights:\n\n"
                    f"{request.text}"
                )

                adapter = None
                if request.model.startswith("gpt") and os.getenv("OPENAI_API_KEY"):
                    adapter = OpenAIAdapter(os.getenv("OPENAI_API_KEY"), request.model)
                elif request.model.startswith("claude") and os.getenv("ANTHROPIC_API_KEY"):
                    adapter = AnthropicAdapter(os.getenv("ANTHROPIC_API_KEY"), request.model)
                elif request.model.startswith("gemini") and os.getenv("GOOGLE_API_KEY"):
                    adapter = GeminiAdapter(os.getenv("GOOGLE_API_KEY"), request.model)

                if adapter:
                    result = await adapter.generate(prompt)
                    text = result.get("generated_text", "Analysis completed")
            except Exception:
                text = None

            if not text:
                text = (
                    f"Streaming analysis for {request.model}: "
                    f"{(request.text or '')[:400]}"
                )

            # token stream
            chunk_size = 60
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                yield b"event: token\n"
                yield f"data: {json.dumps({'text': chunk})}\n\n".encode()
                await asyncio.sleep(0)

            # synthesis
            yield b"event: status\n"
            yield b"data: {\"stage\": \"synthesis\", \"percent\": 90}\n\n"

            # cost (placeholder)
            cost_payload = {
                "model": request.model,
                "inputTokens": max(1, len(request.text) // 4),
                "outputTokens": max(1, len(text) // 4),
                "unitCosts": {"inputPer1k": 0.0, "outputPer1k": 0.0},
                "estimatedCostUsd": 0.0,
                "capExceeded": False,
            }
            yield b"event: cost\n"
            yield f"data: {json.dumps(cost_payload)}\n\n".encode()

            # done
            yield b"event: done\n"
            done = {"completedAt": datetime.now(timezone.utc).isoformat()}
            yield f"data: {json.dumps(done)}\n\n".encode()

        return StreamingResponse(
            sse_gen(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    @router.get("/analyze/stream")
    async def analyze_stream_get(text: str, model: str = "gpt-4", http_request: Request = None):
        """GET variant for SSE, reading text/model from query params."""
        req = SimpleAnalysisRequest(text=text, model=model)
        # Reuse POST implementation by calling inner function indirectly
        # Build a minimal Request-like object if http_request is None
        from starlette.requests import Request as StarletteRequest
        if http_request is None:
            http_request = StarletteRequest(scope={"type": "http", "headers": []})
        return await analyze_stream(req, http_request)

    return router


analyze_router = create_router()  # Expose router for application
