# API Reference

Code reference for the Enterprise RAG System.

## Core Modules

### ingestion.py

#### DocumentLoader
```python
class DocumentLoader:
    def load_file(file_path: str) -> List[Document]:
        """Load a markdown file into Document objects."""
```

#### TextCleaner
```python
class TextCleaner:
    def clean(text: str) -> str:
        """Clean and sanitize text."""
```

#### TextSplitter
```python
class TextSplitter:
    def __init__(chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize text splitter."""
    
    def split_documents(documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
```

### vectorizer.py

#### EmbeddingModel
```python
class EmbeddingModel:
    def __init__(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedding model."""
    
    def embed_query(text: str) -> List[float]:
        """Embed a query string."""
    
    def embed_documents(texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
```

#### VectorStoreManager
```python
class VectorStoreManager:
    def __init__(embedding_model: EmbeddingModel):
        """Initialize vector store manager."""
    
    def create_index(documents: List[Document]):
        """Create FAISS index from documents."""
    
    def get_retriever(k: int = 8) -> VectorStoreRetriever:
        """Get retriever for similarity search."""
```

### retrieval.py

#### Retriever
```python
class Retriever:
    def __init__(vector_store_manager: VectorStoreManager):
        """Initialize retriever."""
    
    def retrieve(query: str, k: int = 8) -> List[Document]:
        """Retrieve top-k relevant documents."""
```

### rag.py

#### RAGChain
```python
class RAGChain:
    def __init__(retriever: Retriever, model_name: str = "llama-3.3-70b-versatile"):
        """Initialize RAG chain."""
    
    def answer(query: str) -> Dict[str, Any]:
        """Generate answer for query.
        
        Returns:
            {
                "answer": str,
                "source_documents": List[Document]
            }
        """
```

## Usage Examples

See [examples/](../examples/) directory for complete examples.
