"""
Tests for document upload functionality.

This module tests the document upload API endpoints, validation, and storage.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import app
from backend.config import Config

client = TestClient(app)

# Test data
TEST_USER = {
    "email": "doc_test@example.com",
    "password": "SecurePassword123!",
    "name": "Document Test User",
}

# Create fixtures directory if it doesn't exist
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
os.makedirs(FIXTURES_DIR, exist_ok=True)

# Create a simple text fixture if it doesn't exist
TEXT_FIXTURE_PATH = os.path.join(FIXTURES_DIR, "sample.txt")
if not os.path.exists(TEXT_FIXTURE_PATH):
    with open(TEXT_FIXTURE_PATH, "w") as f:
        f.write("This is a sample document for testing document upload functionality.")


@pytest.fixture
def registered_user():
    """Register a test user and return the user data."""
    # Register user
    response = client.post("/api/auth/register", json=TEST_USER)

    if response.status_code != status.HTTP_201_CREATED:
        # Try logging in if user already exists
        login_response = client.post(
            "/api/auth/login",
            json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
        )
        assert login_response.status_code == status.HTTP_200_OK
        return login_response.json()

    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """Get authentication headers for the test user."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )

    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_text_file():
    """Create a sample text file for upload testing."""
    with open(TEXT_FIXTURE_PATH, "rb") as f:
        content = f.read()
    return content


@pytest.fixture
def mock_document_processor():
    """Mock the document processor for testing."""
    with patch("backend.services.document_processor.process_document") as mock:
        # Mock successful processing
        mock.return_value = {
            "success": True,
            "document_id": "test-doc-123",
            "text_content": "This is a sample document for testing.",
            "word_count": 8,
            "metadata": {
                "filename": "sample.txt",
                "content_type": "text/plain",
                "size_bytes": 100,
            },
        }
        yield mock


def test_document_upload_endpoint_exists(client):
    """Test that the document upload endpoint exists."""
    response = client.options("/api/upload-document")
    assert response.status_code != status.HTTP_404_NOT_FOUND


def test_document_upload_requires_auth(client, sample_text_file):
    """Test that document upload requires authentication."""
    files = {"file": ("sample.txt", sample_text_file, "text/plain")}

    response = client.post("/api/upload-document", files=files)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_document_upload_text(
    client, auth_headers, sample_text_file, mock_document_processor
):
    """Test uploading a text document."""
    files = {"file": ("sample.txt", sample_text_file, "text/plain")}

    response = client.post("/api/upload-document", files=files, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "document_id" in response.json()
    assert response.json()["document_id"] == "test-doc-123"
    assert "filename" in response.json()
    assert response.json()["filename"] == "sample.txt"

    # Verify document processor was called
    mock_document_processor.assert_called_once()


def test_document_upload_without_file(client, auth_headers):
    """Test uploading without a file."""
    response = client.post("/api/upload-document", files={}, headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()
    assert "file" in response.json()["error"].lower()


def test_document_upload_empty_file(client, auth_headers):
    """Test uploading an empty file."""
    files = {"file": ("empty.txt", b"", "text/plain")}

    response = client.post("/api/upload-document", files=files, headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.json()
    assert "empty" in response.json()["error"].lower()


def test_document_retrieval(
    client, auth_headers, sample_text_file, mock_document_processor
):
    """Test retrieving an uploaded document."""
    # Upload a document first
    files = {"file": ("sample.txt", sample_text_file, "text/plain")}

    upload_response = client.post(
        "/api/upload-document", files=files, headers=auth_headers
    )

    assert upload_response.status_code == status.HTTP_200_OK
    document_id = upload_response.json()["document_id"]

    # Mock the document retrieval
    with patch("backend.services.document_service.get_document") as mock_get_document:
        mock_get_document.return_value = {
            "document_id": document_id,
            "filename": "sample.txt",
            "content_type": "text/plain",
            "size_bytes": 100,
            "upload_time": "2025-05-13T10:00:00Z",
            "status": "processed",
            "word_count": 8,
        }

        # Retrieve the document
        response = client.get(f"/api/documents/{document_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "document_id" in response.json()
        assert response.json()["document_id"] == document_id
        assert "filename" in response.json()
        assert response.json()["filename"] == "sample.txt"
        assert "content_type" in response.json()
        assert "upload_time" in response.json()


def test_document_retrieval_not_found(client, auth_headers):
    """Test retrieving a non-existent document."""
    non_existent_id = "non-existent-doc-id"

    # Mock the document retrieval to return None
    with patch("backend.services.document_service.get_document") as mock_get_document:
        mock_get_document.return_value = None

        response = client.get(f"/api/documents/{non_existent_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.json()
        assert "not found" in response.json()["error"].lower()


def test_document_list(client, auth_headers):
    """Test listing user documents."""
    # Mock the document list service
    with patch("backend.services.document_service.get_user_documents") as mock_get_docs:
        mock_get_docs.return_value = [
            {
                "document_id": "doc-1",
                "filename": "sample1.txt",
                "content_type": "text/plain",
                "size_bytes": 100,
                "upload_time": "2025-05-13T10:00:00Z",
                "status": "processed",
            },
            {
                "document_id": "doc-2",
                "filename": "sample2.txt",
                "content_type": "text/plain",
                "size_bytes": 150,
                "upload_time": "2025-05-13T11:00:00Z",
                "status": "processed",
            },
        ]

        response = client.get("/api/documents", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "documents" in response.json()
        assert len(response.json()["documents"]) == 2
        assert response.json()["documents"][0]["document_id"] == "doc-1"
        assert response.json()["documents"][1]["document_id"] == "doc-2"


def test_document_delete(client, auth_headers):
    """Test deleting a document."""
    document_id = "doc-to-delete"

    # Mock the document deletion service
    with patch("backend.services.document_service.delete_document") as mock_delete:
        mock_delete.return_value = True

        response = client.delete(f"/api/documents/{document_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.json()
        assert response.json()["success"] is True
        assert "message" in response.json()

        # Verify deletion was called
        mock_delete.assert_called_once_with(document_id, TEST_USER["email"])


def test_document_delete_not_found(client, auth_headers):
    """Test deleting a non-existent document."""
    non_existent_id = "non-existent-doc-id"

    # Mock the document deletion service to return False (not found)
    with patch("backend.services.document_service.delete_document") as mock_delete:
        mock_delete.return_value = False

        response = client.delete(
            f"/api/documents/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.json()
        assert "not found" in response.json()["error"].lower()


if __name__ == "__main__":
    pytest.main(["-xvs", "test_document_upload.py"])
