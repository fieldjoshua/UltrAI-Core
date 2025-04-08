from fastapi import Request
from fastapi.responses import JSONResponse
from log import logger


@app.post("/api/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        selected_models = data.get("selectedModels", [])
        ultra_model = data.get("ultraModel")
        pattern_name = data.get("pattern", "Confidence Analysis")
        options = data.get("options", {})

        # Map frontend pattern names to backend pattern keys
        pattern_map = {
            "Confidence Analysis": "confidence",
            "Critique": "critique",
            "Gut Check": "gut",
            "Scenario Analysis": "scenario",
            "Stakeholder Vision": "stakeholder",
            "Systems Mapper": "systems",
            "Time Horizon": "time",
            "Innovation Bridge": "innovation",
        }

        pattern_key = pattern_map.get(pattern_name, "confidence")

        # Get the pattern
        analyzer = AnalysisPatterns()
        pattern = analyzer.get_pattern(pattern_key)

        if not pattern:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Invalid pattern: {pattern_name}"},
            )

        # Initialize the orchestrator with the pattern
        orchestrator = TriLLMOrchestrator(selected_models, ultra_model, pattern)

        # Process the prompt with the selected pattern
        result = await orchestrator.process(prompt, options)

        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in /api/analyze: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred during analysis: {str(e)}"},
        )
