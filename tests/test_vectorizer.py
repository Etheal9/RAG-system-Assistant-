import pytest
from unittest.mock import MagicMock, patch
from src.vectorizer import EmbeddingModel

def test_embedding_model_initialization():
    with patch("src.vectorizer.HuggingFaceEmbeddings") as MockEmbeddings:
        model = EmbeddingModel()
        MockEmbeddings.assert_called_once()

def test_get_embedding():
    with patch("src.vectorizer.HuggingFaceEmbeddings") as MockEmbeddings:
        mock_instance = MockEmbeddings.return_value
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        model = EmbeddingModel()
        embedding = model.embed_query("test query")
        
        assert embedding == [0.1, 0.2, 0.3]
        mock_instance.embed_query.assert_called_with("test query")

def test_get_documents_embedding():
    with patch("src.vectorizer.HuggingFaceEmbeddings") as MockEmbeddings:
        mock_instance = MockEmbeddings.return_value
        mock_instance.embed_documents.return_value = [[0.1], [0.2]]
        
        model = EmbeddingModel()
        embeddings = model.embed_documents(["doc1", "doc2"])
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1]
        mock_instance.embed_documents.assert_called_with(["doc1", "doc2"])

from src.vectorizer import VectorStoreManager
from langchain_core.documents import Document

def test_vector_store_manager_create():
    with patch("src.vectorizer.FAISS") as MockFAISS:
        mock_embedding_model = MagicMock()
        manager = VectorStoreManager(embedding_model=mock_embedding_model)
        
        docs = [Document(page_content="test", metadata={"source": "test"})]
        manager.create_index(docs)
        
        MockFAISS.from_documents.assert_called_once_with(
            docs, mock_embedding_model.embeddings
        )

def test_vector_store_manager_add():
    with patch("src.vectorizer.FAISS") as MockFAISS:
        mock_embedding_model = MagicMock()
        manager = VectorStoreManager(embedding_model=mock_embedding_model)
        
        # Mock internal vector store
        manager.vector_store = MockFAISS.return_value
        
        docs = [Document(page_content="test2")]
        manager.add_documents(docs)
        
        manager.vector_store.add_documents.assert_called_once_with(docs)

def test_vector_store_metadata():
    """Verify that metadata is preserved when adding to vector store."""
    with patch("src.vectorizer.FAISS") as MockFAISS:
        mock_embedding_model = MagicMock()
        manager = VectorStoreManager(embedding_model=mock_embedding_model)
        
        docs = [
            Document(page_content="chunk1", metadata={"source": "file.md", "chunk_id": 1}),
            Document(page_content="chunk2", metadata={"source": "file.md", "chunk_id": 2})
        ]
        
        manager.create_index(docs)
        
        # Verify call args
        args, _ = MockFAISS.from_documents.call_args
        passed_docs = args[0]
        assert passed_docs[0].metadata["source"] == "file.md"
        assert passed_docs[0].metadata["chunk_id"] == 1
