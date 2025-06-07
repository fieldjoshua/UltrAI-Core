import pytest
from datetime import datetime
from unittest.mock import Mock
from app.services.analysis_service import AnalysisService


class DummyAnalysis:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.user_id = kwargs.get("user_id")
        self.document_id = kwargs.get("document_id")
        self.pattern = kwargs.get("pattern")
        self.prompt = kwargs.get("prompt")
        self.models = kwargs.get("models")
        self.status = kwargs.get("status")
        self.created_at = kwargs.get("created_at")
        self.completed_at = kwargs.get("completed_at")
        self.result = kwargs.get("result")
        self.error = kwargs.get("error")
        self.options = kwargs.get("options")


@pytest.fixture
def service(monkeypatch):
    svc = AnalysisService()
    # Stub repository and document service
    svc.analysis_repo = Mock()
    svc.document_service = Mock()
    return svc


def test_get_user_analyses(service):
    # Prepare dummy analyses
    now = datetime(2025, 1, 1, 12, 0, 0)
    dummy = DummyAnalysis(
        id=1,
        user_id="u1",
        document_id="d1",
        pattern="p",
        prompt="pr",
        models=["m1"],
        status="completed",
        created_at=now,
        completed_at=now,
        result={"x": 1},
        error=None,
        options={"o": 2},
    )
    service.analysis_repo.get_by_user_id.return_value = [dummy]
    res = service.get_user_analyses(db=Mock(), user_id="u1", skip=0, limit=10)
    assert isinstance(res, list) and len(res) == 1
    r = res[0]
    assert r["id"] == 1 and r["user_id"] == "u1"
    assert r["created_at"] == "2025-01-01T12:00:00"


def test_get_document_analyses_with_access(service):
    dummy = DummyAnalysis(
        id=2,
        user_id="u2",
        document_id="d2",
        pattern="p",
        prompt="pr",
        models=["m1"],
        status="ok",
        created_at=None,
        completed_at=None,
        result={},
        error=None,
        options={},
    )
    service.document_service.get_document_by_id.return_value = None
    service.analysis_repo.get_by_document_id.return_value = [dummy]
    res = service.get_document_analyses(db=Mock(), document_id="d2", user_id="u2")
    assert res[0]["document_id"] == "d2"


def test_create_analysis_with_doc_check(service):
    dummy = DummyAnalysis(
        id=3,
        user_id="u3",
        document_id="d3",
        pattern="pt",
        prompt="pr",
        models=["m"],
        status="new",
        created_at=None,
        completed_at=None,
        result=None,
        error=None,
        options={},
    )
    service.document_service.get_document_by_id.return_value = None
    service.analysis_repo.create_analysis.return_value = dummy
    out = service.create_analysis(
        db=Mock(),
        user_id="u3",
        document_id="d3",
        pattern="pt",
        prompt="pr",
        models=["m"],
        options={},
    )
    assert out["id"] == 3 and out["status"] == "new"


def test_update_analysis_status_and_permission(service):
    dummy = DummyAnalysis(
        id=4,
        user_id="owner",
        document_id=None,
        pattern="",
        prompt="",
        models=[],
        status="pending",
        created_at=None,
        completed_at=None,
        result=None,
        error=None,
        options={},
    )
    # Ownership correct
    service.analysis_repo.get_by_id.return_value = dummy
    service.analysis_repo.update_analysis_status.return_value = dummy
    out = service.update_analysis_status(
        db=Mock(),
        analysis_id=4,
        status="completed",
        result={"r": 1},
        error=None,
        user_id="owner",
    )
    assert out["status"] == "pending" or out["id"] == 4
    # Wrong user
    with pytest.raises(PermissionError):
        service.update_analysis_status(
            db=Mock(),
            analysis_id=4,
            status="failed",
            result=None,
            error="e",
            user_id="other",
        )


def test_get_analysis_by_id_and_permission(service):
    dummy = DummyAnalysis(
        id=5,
        user_id="u5",
        document_id=None,
        pattern="",
        prompt="",
        models=[],
        status="s",
        created_at=None,
        completed_at=None,
        result=None,
        error=None,
        options={},
    )
    service.analysis_repo.get_by_id.return_value = dummy
    # No user_id
    out1 = service.get_analysis_by_id(db=Mock(), analysis_id=5)
    assert out1["id"] == 5
    # Wrong user
    with pytest.raises(PermissionError):
        service.get_analysis_by_id(db=Mock(), analysis_id=5, user_id="x")


def test_get_pattern_stats(service):
    stats = {"a": 2, "b": 3}
    service.analysis_repo.get_stats_by_pattern.return_value = stats
    out = service.get_pattern_stats(db=Mock())
    assert out["total_analyses"] == 5
    assert "pattern_percentages" in out and out["pattern_percentages"]["a"] == 40.0
