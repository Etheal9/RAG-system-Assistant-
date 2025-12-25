# Usage Guide

Comprehensive guide to using the Enterprise RAG System.

## Table of Contents
- [Quick Start](#quick-start)
- [Web Interface](#web-interface)
- [Command Line Interface](#command-line-interface)
- [Adding Documents](#adding-documents)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)

## Quick Start

### 1. Start the Application

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Start Streamlit app
streamlit run app.py
```

### 2. Open in Browser

The app automatically opens at `http://localhost:8501`

### 3. Ask a Question

Type your question in the chat input and press Enter.

**Example:**
```
What is RAG and why is it important?
```

The system will:
1. Search your documents
2. Find relevant chunks
3. Generate an answer
4. Show source documents

---

## Web Interface

### Main Features

#### 1. Chat Interface

- **Ask questions** in natural language
- **View answers** with source attribution
- **See chat history** - all previous Q&A pairs
- **Clear history** - start fresh conversation

#### 2. Source Citations

Click **"View Sources"** to see:
- Which documents were used
- Relevant text snippets
- Document names

#### 3. Sidebar Information

- **System status** - Groq + HuggingFace
- **Loaded documents** - count and list
- **Total chunks** - indexed pieces
- **Clear chat** button

### Example Workflow

1. **Start the app**
```bash
streamlit run app.py
```

2. **Wait for initialization**
- System loads documents
- Creates embeddings
- Builds index
- Shows "✅ System Ready!"

3. **Ask your first question**
```
How does chunking affect retrieval quality?
```

4. **Review the answer**
- Read the generated response
- Click "View Sources" to see which documents were used
- Verify the answer is grounded in your documents

5. **Ask follow-up questions**
```
What are the best chunk sizes?
```

6. **Clear history when done**
- Click "🔄 Clear Chat History" in sidebar

---

## Command Line Interface

For programmatic access or scripting:

### Basic Usage

```bash
python src/main.py
```

This starts an interactive CLI:
```
=== System Ready! (Type 'exit' to quit) ===

Enter your question: What is RAG?

Processing...

>> ANSWER:
RAG (Retrieval-Augmented Generation) is...

>> SOURCES:
   - Enterprise RAG System .md
   - The Science of Chunking,md
```

### Programmatic Usage

```python
from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

# Initialize system
loader = DocumentLoader()
cleaner = TextCleaner()
splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

# Load documents
docs = loader.load_file("data/my_document.md")
for doc in docs:
    doc.page_content = cleaner.clean(doc.page_content)
chunks = splitter.split_documents(docs)

# Create index
embedding_model = EmbeddingModel()
manager = VectorStoreManager(embedding_model)
manager.create_index(chunks)

# Create RAG chain
retriever = Retriever(vector_store_manager=manager)
rag_chain = RAGChain(retriever=retriever)

# Ask questions
result = rag_chain.answer("What is this document about?")
print(result["answer"])
```

---

## Adding Documents

### Supported Formats

Currently supported:
- **Markdown** (`.md`)
- **Text** (`.txt`) - with minor code changes

### Adding New Documents

1. **Place files in `data/` folder**
```bash
# Windows
copy my_document.md "data\"

# macOS/Linux
cp my_document.md data/
```

2. **Restart the Streamlit app**
```bash
# Stop with Ctrl+C
# Restart
streamlit run app.py
```

3. **Verify loading**
- Check sidebar for document count
- Should show your new file

### Document Best Practices

**Good documents:**
- Clear structure with headings
- Focused topics
- 1-100 pages
- Markdown formatting

**Avoid:**
- Very large files (>10MB) - split them
- Binary formats (PDF, DOCX) - convert to markdown
- Scanned images - use OCR first

### Example Document Structure

```markdown
# Main Topic

## Subtopic 1

Content about subtopic 1...

## Subtopic 2

Content about subtopic 2...

### Details

More specific information...
```

---

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (future)
# CHUNK_SIZE=500
# RETRIEVAL_K=8
```

### Retrieval Settings

Edit `src/retrieval.py`:

```python
def retrieve(self, query: str, k: int = 8):  # Change k value
```

**k values:**
- `k=4` - Fast, less context
- `k=8` - Balanced (default)
- `k=12` - Slower, more context

### Chunking Settings

Edit `app.py` or `src/main.py`:

```python
splitter = TextSplitter(
    chunk_size=500,      # Tokens per chunk
    chunk_overlap=50     # Overlap between chunks
)
```

**Chunk size guidelines:**
- `300-400` - Short, focused chunks
- `500-600` - Balanced (default)
- `800-1000` - Long, more context

### Model Settings

Edit `src/rag.py`:

```python
def __init__(self, retriever: Retriever, model_name: str = "llama-3.3-70b-versatile"):
```

**Available Groq models:**
- `llama-3.3-70b-versatile` - Best quality (default)
- `llama-3.1-70b-versatile` - Fast
- `mixtral-8x7b-32768` - Long context

---

## Advanced Usage

### Custom Prompts

Edit `src/prompts.py`:

```python
RAG_SYSTEM_PROMPT = """You are a rag system document assistance...
```

Modify to change:
- Tone (formal, casual, technical)
- Response format (bullet points, paragraphs)
- Refusal behavior

### Evaluation

Run evaluation on test dataset:

```bash
python src/evaluate.py
```

Output shows:
- Refusal accuracy
- Answer quality
- Source attribution

### Retrieval Verification

Test retrieval quality:

```bash
python src/verify_retrieval.py
```

Shows:
- Retrieved chunks
- Similarity scores
- Source documents

### Batch Processing

Process multiple questions:

```python
questions = [
    "What is RAG?",
    "How does chunking work?",
    "What are best practices?"
]

for q in questions:
    result = rag_chain.answer(q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

---

## Tips & Best Practices

### 1. Document Quality

- ✅ Use clear, well-structured documents
- ✅ Include relevant metadata
- ✅ Keep documents focused on specific topics
- ❌ Don't mix unrelated content

### 2. Question Formulation

- ✅ Ask specific, focused questions
- ✅ Use keywords from your documents
- ✅ Provide context if needed
- ❌ Don't ask overly broad questions

### 3. Performance Optimization

- ✅ Start with fewer documents, add more gradually
- ✅ Use appropriate chunk sizes for your content
- ✅ Adjust k based on your needs
- ❌ Don't load unnecessary documents

### 4. Answer Verification

- ✅ Always check source citations
- ✅ Verify answers against original documents
- ✅ Report issues if answers seem incorrect
- ❌ Don't trust answers blindly

---

## Common Use Cases

### 1. Technical Documentation Q&A

```
Q: How do I configure the API endpoint?
A: [Answer with code examples from docs]
```

### 2. Research Paper Analysis

```
Q: What methodology did the authors use?
A: [Answer citing specific sections]
```

### 3. Internal Knowledge Base

```
Q: What is our policy on remote work?
A: [Answer from company policies]
```

### 4. Educational Content

```
Q: Explain the concept of embeddings
A: [Answer from educational materials]
```

---

## Next Steps

- Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Check [API.md](API.md) for code reference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [examples/](../examples/) for code samples

---

**Happy querying!** 🚀
