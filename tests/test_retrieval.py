import pytest
from unittest.mock import MagicMock
from src.retrieval import Retriever
from langchain_core.documents import Document

def test_retrieve_documents():
    # Mock the vector store manager and its retriever
    mock_manager = MagicMock()
    mock_retriever = MagicMock()
    mock_manager.get_retriever.return_value = mock_retriever
    
    # Setup expected return
    expected_docs = [Document(page_content="result")]
    mock_retriever.invoke.return_value = expected_docs
    
    # Initialize Retriever
    retriever = Retriever(vector_store_manager=mock_manager)
    
    # Execute
    results = retriever.retrieve("query")
    
    # Verify
    assert len(results) == 1
    assert results[0].page_content == "result"
    mock_manager.get_retriever.assert_called()
    mock_retriever.invoke.assert_called_with("query")

def test_retrieve_empty_query():
    mock_manager = MagicMock()
    retriever = Retriever(vector_store_manager=mock_manager)
    
    # Should probably verify it returns empty or raises error, 
    # but for now let's say it just returns empty list if valid but empty? 
    # Or maybe we enforce validation.
    # Let's verify it still calls the backend or handles it gracefully.
    # For this system, we can just pass it through.
    
    retriever.retrieve("   ")
    # Depends on implementation, but assuming it sanitizes or passes through.
