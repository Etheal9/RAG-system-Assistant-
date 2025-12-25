import pytest
from unittest.mock import MagicMock, patch
from src.rag import RAGChain

def test_fallback_when_retrieval_empty():
    """Verify that if retrieval returns no docs, we still get a safe response."""
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = []
    
    with patch("src.rag.ChatGroq") as MockChat:
        mock_llm = MockChat.return_value
        # We rely on the system prompt to instruct the LLM to say "I don't know"
        # Since we use a real LLM prompt in the chain, we expect the output to be what the LLM returns.
        # Here we mock the LLM to obey the instruction for the test.
        mock_llm.invoke.return_value.content = "I don't know based on the provided documents."
        
        chain = RAGChain(retriever=mock_retriever)
        response = chain.answer("What is the secret?")
        
        assert "I don't know" in response["answer"]
        assert len(response["source_documents"]) == 0
        
        # Verify that we passed empty context to the prompt
        # We can inspect the calls to invoke if needed
