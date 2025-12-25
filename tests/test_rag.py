import pytest
from unittest.mock import MagicMock, patch
from src.rag import RAGChain
from langchain_core.documents import Document

def test_rag_chain_answer():
    # Mock Retriever
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [Document(page_content="context info")]
    
    # Mock LLM (ChatGroq) response
    with patch("src.rag.ChatGroq") as MockChat:
        mock_llm_instance = MockChat.return_value
        mock_llm_instance.invoke.return_value.content = "Answer based on context"
        
        chain = RAGChain(retriever=mock_retriever)
        
        # Test "answer" method (simple interface)
        response = chain.answer("test query")
        
        assert response["answer"] == "Answer based on context"
        assert len(response["source_documents"]) == 1
        
        # Verify interactions
        mock_retriever.retrieve.assert_called_with("test query")
        # Verify LLM call - hard to check exact prompt structure without more complex matching,
        # but we can check it was called.
        mock_llm_instance.invoke.assert_called()

def test_rag_chain_no_context():
    # If retriever returns nothing, should we still ask LLM?
    # PRD says "Refuse when context is insufficient".
    # Ideally, if context is empty, we might skip LLM or let LLM decide.
    # Current prompt instructs LLM to say "I don't know".
    
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = []
    
    with patch("src.rag.ChatOpenAI") as MockChat:
        mock_llm_instance = MockChat.return_value
        mock_llm_instance.invoke.return_value.content = "I don't know based on the provided documents."
        
        chain = RAGChain(retriever=mock_retriever)
        response = chain.answer("test query")
        
        # Verify context sent was empty string or similar
        args, _ = mock_llm_instance.invoke.call_args
        # We assume the prompt is passed to invoke.
