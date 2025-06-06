import pytest
from unittest.mock import AsyncMock, patch
from app.services.prompt_service import PromptService, Template, PromptRequest
from app.services.model_registry import ModelRegistry
from app.services.orchestration_service import OrchestrationService


@pytest.fixture
def services():
    model_registry = ModelRegistry()
    orchestration_service = OrchestrationService(model_registry=model_registry)
    prompt_service = PromptService(
        model_registry=model_registry, orchestration_service=orchestration_service
    )
    return model_registry, orchestration_service, prompt_service


@pytest.mark.asyncio
async def test_prompt_service_integration(services):
    model_registry, orchestration_service, prompt_service = services

    # Register a template
    template = Template(
        name="integration_test",
        description="Integration test template",
        template="Test {variable}",
        variables=["variable"],
    )
    prompt_service.register_template(template)

    # Process a prompt
    request = PromptRequest(
        template_name="integration_test",
        variables={"variable": "value"},
        models=["test-model"],
    )

    # Patch OrchestrationService.process_prompt using AsyncMock
    with patch.object(
        orchestration_service, "process_prompt", new_callable=AsyncMock
    ) as mock_process_prompt:
        mock_process_prompt.return_value = {"result": "success"}
        result = await prompt_service.process_prompt(request)
        assert result["result"] == "success"
