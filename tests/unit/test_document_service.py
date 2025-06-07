import datetime
import pytest
from app.services.document_service import DocumentService
from types import SimpleNamespace


class DummyDoc:
    def __init__(self):
        self.id = "doc1"
        self.user_id = "user1"
        self.filename = "file.txt"
        self.content_type = "text/plain"
        self.size_bytes = 10
        self.created_at = datetime.datetime.utcnow()
        self.processed_at = datetime.datetime.utcnow()
        self.status = "ready"
        self.word_count = 5
        self.chunk_count = 2
        self.embedding_model = "model"


@pytest.fixture
def service(monkeypatch):
    svc = DocumentService()
    rep = SimpleNamespace(
        get_user_documents=lambda db, uid, skip, lim: [DummyDoc()],
        get_by_id=lambda db, id, raise_if_not_found: DummyDoc(),
        delete=lambda db, id: None,
    )
    chunk_rep = SimpleNamespace(
        count_chunks_by_document_id=lambda db, id: 3,
        delete_document_chunks=lambda db, id: 3,
        get_chunks_by_document_id=lambda db, id, skip, lim: [],
    )
    monkeypatch.setattr(svc, "document_repo", rep)
    monkeypatch.setattr(svc, "chunk_repo", chunk_rep)
    return svc


def test_get_user_documents(service):
    docs = service.get_user_documents(db=None, user_id="user1")
    assert isinstance(docs, list)
    assert docs[0]["id"] == "doc1"


def test_get_document_by_id(service):
    doc = service.get_document_by_id(db=None, document_id="doc1", user_id="user1")
    assert doc["id"] == "doc1"
    assert doc["actual_chunk_count"] == 3


def test_delete_document(service):
    result = service.delete_document(db=None, document_id="doc1", user_id="user1")
    assert result["status"] == "deleted"
