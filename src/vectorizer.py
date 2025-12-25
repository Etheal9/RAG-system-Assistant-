from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name (str): The name of the HuggingFace embedding model to use.
        """
        if not model_name:
             model_name = "sentence-transformers/all-MiniLM-L6-v2"
        # Runs locally, no API key needed
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query string.
        
        Args:
            text (str): The text to embed.
            
        Returns:
            List[float]: The embedding vector.
        """
        return self.embeddings.embed_query(text)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            documents (List[str]): List of texts to embed.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        return self.embeddings.embed_documents(documents)

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class VectorStoreManager:
    def __init__(self, embedding_model: EmbeddingModel):
        """
        Initialize the VectorStoreManager.
        
        Args:
            embedding_model (EmbeddingModel): The embedding model wrapper.
        """
        self.embedding_model = embedding_model
        self.vector_store = None

    def create_index(self, documents: List[Document]):
        """
        Create a new FAISS index from documents.
        
        Args:
            documents (List[Document]): The documents to index.
        """
        self.vector_store = FAISS.from_documents(
            documents, self.embedding_model.embeddings
        )

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the existing index.
        
        Args:
            documents (List[Document]): The documents to add.
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_index first.")
        self.vector_store.add_documents(documents)
    
    def get_retriever(self, k: int = 4):
        """Returns a retriever from the vector store."""
        if self.vector_store is None:
             raise ValueError("Vector store not initialized.")
        return self.vector_store.as_retriever(search_kwargs={"k": k})
