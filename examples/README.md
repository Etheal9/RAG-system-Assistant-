# Examples

This directory contains code examples demonstrating how to use the Enterprise RAG System.

## Available Examples

### 1. basic_usage.py
Basic end-to-end usage of the RAG system.

**Run:**
```bash
python examples/basic_usage.py
```

**Demonstrates:**
- Loading documents
- Creating vector index
- Asking questions
- Getting answers with sources

### 2. custom_documents.py
Working with your own custom documents.

**Run:**
```bash
python examples/custom_documents.py
```

**Demonstrates:**
- Loading specific files
- Processing custom content
- Querying custom knowledge base

### 3. evaluation_example.py
Running evaluation on the system.

**Run:**
```bash
python examples/evaluation_example.py
```

**Demonstrates:**
- Creating test datasets
- Running evaluations
- Measuring accuracy

## Prerequisites

All examples require:
1. Virtual environment activated
2. Dependencies installed (`pip install -r requirements.txt`)
3. `.env` file with `GROQ_API_KEY`

## Modifying Examples

Feel free to modify these examples for your use case:
- Change document paths
- Adjust chunk sizes
- Modify questions
- Add custom logic

## More Examples

For more advanced usage, see:
- [docs/USAGE.md](../docs/USAGE.md) - Comprehensive usage guide
- [docs/API.md](../docs/API.md) - API reference
- [src/](../src/) - Source code with docstrings
