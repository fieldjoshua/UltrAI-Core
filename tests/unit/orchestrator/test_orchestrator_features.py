import base64
import pytest

from app.services.minimal_orchestrator import MinimalOrchestrator
from app.services.output_formatter import _decrypt

pytestmark = pytest.mark.asyncio


class DummyOrchestrator(MinimalOrchestrator):
    """Subclass with a stubbed _call_model to avoid external API calls."""

    async def _call_model(self, model_name: str, prompt: str, stage: str = "initial"):
        # Return a deterministic dummy response; include stage for uniqueness.
        return {"response": f"{model_name}-{stage}-RESP", "time": 0.1}


@pytest.fixture
def orch():
    return DummyOrchestrator()


async def test_cost_estimate_present(orch):
    res = await orch.orchestrate("hello", ["gpt4o", "claude37"], ultra_model="gpt4o")
    assert "estimated_cost_usd" in res["performance"]
    assert isinstance(res["performance"]["estimated_cost_usd"], float)


async def test_plain_text_format(orch):
    prompt = "## Heading\n**bold** text"
    res = await orch.orchestrate(
        prompt,
        ["gpt4o", "claude37"],
        ultra_model="gpt4o",
        response_format="text",
    )
    ultra = res["ultra_response"]
    assert "#" not in ultra and "*" not in ultra


async def test_encryption_round_trip(orch):
    from app.config import ORCH_CONFIG

    key = "secretkey"
    ORCH_CONFIG.ENCRYPTION_KEY = key  # type: ignore

    res = await orch.orchestrate(
        "hello",
        ["gpt4o", "claude37"],
        ultra_model="gpt4o",
        encrypt=True,
    )
    enc = res["ultra_response"]
    # Ensure it's base64-ish
    base64.b64decode(enc)
    assert _decrypt(enc, key)  # decrypt returns string


async def test_no_model_access_redaction(orch):
    res = await orch.orchestrate(
        "hello",
        ["gpt4o", "claude37"],
        ultra_model="gpt4o",
        no_model_access=True,
    )
    assert res["ultra_response"].startswith("[REDACTED")
    assert res.get("_note")
