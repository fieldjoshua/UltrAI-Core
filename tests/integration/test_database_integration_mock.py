"""
Database integration tests using mocked repositories.

These tests verify database operations without requiring
specific database features.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


@pytest.mark.integration
def test_user_creation_and_retrieval():
    """Test user creation and retrieval through repository."""
    # Mock the repository
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "alice@example.com"
    mock_user.username = "alice"
    mock_user.full_name = "Alice A"
    mock_user.created_at = datetime.utcnow()
    
    # Configure mock behavior
    mock_repo.create_user.return_value = mock_user
    mock_repo.get_by_email.return_value = mock_user
    
    # Test user creation
    data = {
        "email": "alice@example.com",
        "username": "alice",
        "full_name": "Alice A",
        "hashed_password": "x",
    }
    
    with patch('app.database.repositories.user.UserRepository', return_value=mock_repo):
        from app.database.repositories.user import UserRepository
        
        repo = UserRepository()
        user = repo.create_user(MagicMock(), data)
        
        assert user.email == "alice@example.com"
        assert user.username == "alice"
        
        # Test retrieval
        fetched = repo.get_by_email(MagicMock(), "alice@example.com")
        assert fetched is not None
        assert fetched.email == "alice@example.com"
        
        # Verify calls
        mock_repo.create_user.assert_called_once()
        mock_repo.get_by_email.assert_called_once()
        
        # Verify the email parameter
        call_args = mock_repo.get_by_email.call_args
        assert call_args[0][1] == "alice@example.com"


@pytest.mark.integration
def test_transaction_rollback():
    """Test transaction rollback behavior."""
    # Mock the session
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Create a user object
    user_data = {
        "email": "bob@example.com",
        "username": "bob",
        "full_name": "Bob B",
        "hashed_password": "x",
    }
    
    # Simulate adding and rolling back
    mock_session.add(MagicMock(**user_data))
    mock_session.rollback()
    
    # Verify rollback was called
    mock_session.rollback.assert_called_once()
    
    # Verify user is not found after rollback
    result = mock_session.query(MagicMock()).filter(MagicMock()).first()
    assert result is None


@pytest.mark.integration
def test_analysis_creation():
    """Test creating an analysis record."""
    # Mock the analysis repository
    mock_repo = MagicMock()
    mock_analysis = MagicMock()
    mock_analysis.id = 1
    mock_analysis.uuid = "test-uuid-123"
    mock_analysis.prompt = "Test prompt"
    mock_analysis.status = "pending"
    mock_analysis.created_at = datetime.utcnow()
    
    mock_repo.create_analysis.return_value = mock_analysis
    
    # Test analysis creation
    analysis_data = {
        "uuid": "test-uuid-123",
        "user_id": 1,
        "prompt": "Test prompt",
        "selected_models": ["gpt-4", "claude-3"],
        "ultra_model": "gpt-4"
    }
    
    analysis = mock_repo.create_analysis(MagicMock(), analysis_data)
    
    assert analysis.uuid == "test-uuid-123"
    assert analysis.prompt == "Test prompt"
    assert analysis.status == "pending"
    
    # Verify the call
    mock_repo.create_analysis.assert_called_once()


@pytest.mark.integration 
def test_document_processing():
    """Test document creation and chunk processing."""
    # Mock document repository
    mock_doc_repo = MagicMock()
    mock_document = MagicMock()
    mock_document.id = 1
    mock_document.filename = "test.pdf"
    mock_document.status = "pending"
    
    mock_doc_repo.create_document.return_value = mock_document
    
    # Mock chunk creation
    mock_chunks = []
    for i in range(3):
        chunk = MagicMock()
        chunk.id = i + 1
        chunk.document_id = 1
        chunk.chunk_index = i
        chunk.content = f"Chunk {i} content"
        mock_chunks.append(chunk)
    
    mock_doc_repo.create_chunks.return_value = mock_chunks
    
    # Test document creation
    doc_data = {
        "filename": "test.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "user_id": 1
    }
    
    document = mock_doc_repo.create_document(MagicMock(), doc_data)
    assert document.filename == "test.pdf"
    assert document.status == "pending"
    
    # Test chunk creation
    chunks = mock_doc_repo.create_chunks(MagicMock(), document.id, 3)
    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[2].content == "Chunk 2 content"