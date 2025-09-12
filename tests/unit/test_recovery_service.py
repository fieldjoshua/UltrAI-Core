import pytest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_on_timeout(monkeypatch):
    from app.services.recovery_service import RecoveryService, RecoveryType

    service = RecoveryService({"enable_auto_recovery": False})

    # Force selection to api_failure workflow and make first step succeed
    async def ok_health(context):
        return None

    # Monkeypatch to make _execute_workflow run with a failing step first then succeed
    attempts = {"count": 0}

    async def flaky_step(context):
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("transient failure")
        return None

    workflow = service._initialize_workflows()["api_failure"]
    # Replace first step to deterministic version and second step to flaky
    workflow.steps[0].action = ok_health
    workflow.steps[1].action = flaky_step

    # Patch selector to always return our workflow
    monkeypatch.setattr(service, "_select_workflow", lambda et: workflow)

    result = await service.execute_recovery(
        error_type="LLM_TIMEOUT",
        target_service="openai",
        recovery_type=RecoveryType.AUTOMATIC,
    )

    assert result.success is True
    assert result.final_state.value == "succeeded"
    assert attempts["count"] >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_circuit_breaker_integration(monkeypatch):
    from app.services.recovery_service import RecoveryService, RecoveryType

    service = RecoveryService({"enable_auto_recovery": False})

    # Make reset_circuit_breaker step always run without raising
    async def ok_reset(context):
        return None

    workflow = service._initialize_workflows()["api_failure"]
    # Identify the reset breaker step by name
    for step in workflow.steps:
        if step.name == "Reset Circuit Breaker":
            step.requires_confirmation = False
            step.action = ok_reset
            break

    monkeypatch.setattr(service, "_select_workflow", lambda et: workflow)

    result = await service.execute_recovery(
        error_type="LLM_ERROR",
        target_service="openai",
        recovery_type=RecoveryType.AUTOMATIC,
    )

    assert result.success is True

