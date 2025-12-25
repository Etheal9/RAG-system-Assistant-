# System Architecture

Technical overview of the Enterprise RAG System architecture.

## Overview

The Enterprise RAG System is built on a modular architecture with clear separation of concerns:

```
┌─────────────┐
│   User UI   │ (Streamlit / CLI)
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│           RAG Chain (rag.py)                 │
│  ┌────────────┐  ┌────────┐  ┌───────────┐ │
│  │  Retriever │→ │ Prompt │→ │ Groq LLM  │ │
│  └────────────┘  └────────┘  └───────────┘ │
└──────┬───────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│      Retrieval Engine (retrieval.py)         │
│  ┌──────────────────────────────────────┐   │
│  │   FAISS Vector Store (vectorizer.py) │   │
│  └──────────────────────────────────────┘   │
└──────┬───────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│    Ingestion Pipeline (ingestion.py)         │
│  ┌──────┐  ┌─────────┐  ┌──────────────┐   │
│  │ Load │→ │ Clean   │→ │ Chunk        │   │
│  └──────┘  └─────────┘  └──────────────┘   │
└──────┬───────────────────────────────────────┘
       │
┌──────▼──────┐
│  Documents  │ (Markdown files)
└─────────────┘
```

## Core Components

### 1. Ingestion Pipeline (`src/ingestion.py`)

**Purpose:** Load, clean, and chunk documents

**Components:**
- `DocumentLoader`: Loads markdown files
- `TextCleaner`: Sanitizes text
- `TextSplitter`: Splits into chunks

**Flow:**
```python
Raw File → Load → Clean → Split → Chunks
```

**Key Features:**
- Preserves metadata (source, title)
- Configurable chunk size and overlap
- Handles multiple file formats

### 2. Vector Store (`src/vectorizer.py`)

**Purpose:** Convert text to embeddings and store in FAISS

**Components:**
- `EmbeddingModel`: HuggingFace wrapper
- `VectorStoreManager`: FAISS index manager

**Flow:**
```python
Chunks → Embed → Index → FAISS Store
```

**Key Features:**
- Local embeddings (no API calls)
- Fast similarity search
- Metadata preservation

### 3. Retrieval Engine (`src/retrieval.py`)

**Purpose:** Find relevant chunks for queries

**Components:**
- `Retriever`: Semantic search wrapper

**Flow:**
```python
Query → Embed → Search → Top-k Chunks
```

**Key Features:**
- Configurable k (number of results)
- Similarity scoring
- Logging support

### 4. RAG Chain (`src/rag.py`)

**Purpose:** Generate answers using retrieved context

**Components:**
- `RAGChain`: Orchestrates retrieval + generation

**Flow:**
```python
Query → Retrieve → Format Prompt → LLM → Answer
```

**Key Features:**
- Strict grounding
- Refusal logic
- Source attribution

### 5. Prompts (`src/prompts.py`)

**Purpose:** Define system behavior

**Components:**
- `RAG_SYSTEM_PROMPT`: System instructions
- `get_rag_prompt_template()`: Prompt builder

**Key Features:**
- Enforces grounding
- Defines refusal behavior
- Configurable

## Data Flow

### Indexing Flow (Startup)

```
1. Load Documents
   ├─ Read markdown files from data/
   └─ Create Document objects

2. Clean Text
   ├─ Remove extra whitespace
   ├─ Normalize newlines
   └─ Sanitize content

3. Split into Chunks
   ├─ Chunk size: 500 tokens
   ├─ Overlap: 50 tokens
   └─ Preserve metadata

4. Generate Embeddings
   ├─ Model: sentence-transformers/all-MiniLM-L6-v2
   ├─ Dimension: 384
   └─ Local (no API)

5. Build FAISS Index
   ├─ Index type: Flat L2
   ├─ Store vectors + metadata
   └─ Ready for search
```

### Query Flow (Runtime)

```
1. User Query
   └─ "What is RAG?"

2. Embed Query
   ├─ Same model as documents
   └─ 384-dimensional vector

3. Similarity Search
   ├─ FAISS finds top-k chunks
   ├─ k=8 (default)
   └─ Returns chunks + scores

4. Format Prompt
   ├─ System: RAG_SYSTEM_PROMPT
   ├─ Context: Retrieved chunks
   └─ Human: User query

5. Generate Answer
   ├─ Model: Groq Llama 3.3 70B
   ├─ Temperature: 0 (deterministic)
   └─ Returns answer

6. Return Result
   ├─ Answer text
   └─ Source documents
```

## Technology Stack

### Core Framework
- **LangChain**: RAG orchestration
- **Python**: 3.9+

### LLM & Embeddings
- **Groq**: LLM API (Llama 3.3 70B)
- **HuggingFace**: Embeddings (sentence-transformers)

### Vector Database
- **FAISS**: Similarity search

### UI
- **Streamlit**: Web interface

### Testing
- **Pytest**: Unit & integration tests

## Design Decisions

### Why Local Embeddings?

**Pros:**
- No API calls = faster
- No cost for embeddings
- Privacy (data stays local)

**Cons:**
- Requires RAM (~2GB)
- Initial download (~90MB)

**Decision:** Benefits outweigh costs for most users

### Why FAISS?

**Pros:**
- Fast similarity search
- Works locally
- No external dependencies

**Cons:**
- In-memory only
- No persistence (rebuilds on restart)

**Decision:** Speed and simplicity > persistence

### Why Groq?

**Pros:**
- Very fast inference
- Free tier available
- Good model quality

**Cons:**
- Requires API key
- Rate limits

**Decision:** Speed and quality justify API dependency

### Why Streamlit?

**Pros:**
- Easy to build UI
- Python-native
- Good for demos

**Cons:**
- Not production-grade for high traffic
- Limited customization

**Decision:** Perfect for MVP and demos

## Performance Characteristics

### Indexing Performance

| Documents | Chunks | Index Time | Memory |
|-----------|--------|------------|--------|
| 5         | ~100   | ~10s       | ~500MB |
| 10        | ~200   | ~20s       | ~1GB   |
| 50        | ~1000  | ~2min      | ~3GB   |

### Query Performance

| Component | Time | Notes |
|-----------|------|-------|
| Embedding | ~50ms | Local |
| Retrieval | ~10ms | FAISS |
| LLM | ~2s | Groq API |
| **Total** | **~2-3s** | End-to-end |

### Scalability

**Current Limits:**
- Documents: ~100 files
- Total chunks: ~10,000
- Memory: ~4GB RAM

**Future Improvements:**
- Persistent vector store (Chroma, Pinecone)
- Batch processing
- Distributed indexing

## Security Considerations

### API Key Protection

- Stored in `.env` file
- Excluded via `.gitignore`
- Never logged or displayed

### Data Privacy

- Documents stay local
- Embeddings generated locally
- Only queries sent to Groq API

### Input Validation

- File type checking
- Size limits
- Sanitization of user input

## Extension Points

### Adding New Document Types

Edit `src/ingestion.py`:
```python
class DocumentLoader:
    def load_file(self, file_path: str):
        if file_path.endswith('.pdf'):
            # Add PDF support
            pass
```

### Custom Embeddings

Edit `src/vectorizer.py`:
```python
class EmbeddingModel:
    def __init__(self, model_name: str = "your-model"):
        # Use different model
        pass
```

### Different Vector Store

Edit `src/vectorizer.py`:
```python
from langchain_chroma import Chroma

class VectorStoreManager:
    def create_index(self, documents):
        self.vector_store = Chroma.from_documents(...)
```

### Custom LLM

Edit `src/rag.py`:
```python
from langchain_openai import ChatOpenAI

class RAGChain:
    def __init__(self, retriever):
        self.llm = ChatOpenAI(model="gpt-4")
```

## Future Enhancements

### Planned Features

1. **Persistent Storage**
   - Save FAISS index to disk
   - Incremental updates

2. **Advanced Retrieval**
   - Hybrid search (keyword + semantic)
   - Re-ranking
   - Query expansion

3. **Multi-Modal**
   - PDF support
   - Image understanding
   - Table extraction

4. **Production Features**
   - Authentication
   - Rate limiting
   - Monitoring/logging
   - API endpoints

---

**For implementation details, see the source code in `src/`**
