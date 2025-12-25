# Contributing to Enterprise RAG System

Thank you for your interest in contributing! This document provides guidelines for contributing to the Enterprise RAG System.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How to Report Issues](#how-to-report-issues)
- [How to Submit Pull Requests](#how-to-submit-pull-requests)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## How to Report Issues

### Before Submitting an Issue

1. **Search existing issues** to avoid duplicates
2. **Check the documentation** - your question might already be answered
3. **Try the latest version** - the issue may already be fixed

### Submitting a Bug Report

Include:
- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Error messages** or logs
- **Code samples** if applicable

**Example:**
```markdown
**Bug**: Streamlit app crashes when loading large documents

**Steps to Reproduce:**
1. Add a 10MB markdown file to data/
2. Run `streamlit run app.py`
3. App crashes with MemoryError

**Environment:**
- OS: Windows 11
- Python: 3.10.5
- RAM: 8GB

**Error:**
MemoryError: Unable to allocate array...
```

### Suggesting Features

Include:
- **Clear description** of the feature
- **Use case** - why is this needed?
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

## How to Submit Pull Requests

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/yourusername/enterprise-rag-system.git
cd enterprise-rag-system
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

### 3. Make Your Changes

- Follow the [Code Style Guidelines](#code-style-guidelines)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Test the Streamlit app
streamlit run app.py
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git commit -m "Add support for PDF documents

- Implement PDF loader in ingestion.py
- Add pypdf2 to requirements.txt
- Add tests for PDF loading
- Update README with PDF instructions"
```

**Commit message format:**
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (if needed)
- Reference issues: `Fixes #123` or `Closes #456`

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- **Clear title** describing the change
- **Description** of what changed and why
- **Link to related issues**
- **Screenshots** (if UI changes)
- **Testing done**

## Development Setup

### 1. Install Development Dependencies

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install black pytest-cov
```

### 2. Configure Environment

Create `.env` file:
```
GROQ_API_KEY=your_test_api_key
```

### 3. Verify Setup

```bash
# Run tests
pytest tests/

# Run app
streamlit run app.py
```

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized (standard library, third-party, local)

### Type Hints

Use type hints for all functions:

```python
def retrieve(self, query: str, k: int = 8) -> List[Document]:
    """Retrieve relevant documents."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def process_document(file_path: str, chunk_size: int = 500) -> List[str]:
    """
    Process a document into chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of each chunk in tokens
        
    Returns:
        List of text chunks
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    pass
```

### Code Organization

- **One class per file** (unless closely related)
- **Functions before classes**
- **Private methods** start with `_`
- **Constants** in UPPER_CASE

### Example

```python
from typing import List, Optional
from pathlib import Path

# Constants
DEFAULT_CHUNK_SIZE = 500
MAX_RETRIES = 3

# Functions
def load_file(path: Path) -> str:
    """Load file content."""
    pass

# Classes
class DocumentProcessor:
    """Process documents for RAG."""
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """Initialize processor."""
        self.chunk_size = chunk_size
    
    def process(self, text: str) -> List[str]:
        """Process text into chunks."""
        pass
```

## Testing Requirements

### Test Coverage

- **Minimum**: 80% code coverage
- **Target**: 90%+ for core modules

### Test Types

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test full workflows

### Writing Tests

```python
import pytest
from src.ingestion import DocumentLoader

def test_load_markdown_file():
    """Test loading a markdown file."""
    loader = DocumentLoader()
    docs = loader.load_file("test.md")
    
    assert len(docs) > 0
    assert docs[0].page_content != ""

def test_load_nonexistent_file():
    """Test error handling for missing files."""
    loader = DocumentLoader()
    
    with pytest.raises(FileNotFoundError):
        loader.load_file("nonexistent.md")
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_ingestion.py

# Specific test
pytest tests/test_ingestion.py::test_load_markdown_file

# With coverage
pytest tests/ --cov=src --cov-report=html

# Verbose
pytest tests/ -v
```

## Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (README, docstrings)
- [ ] No sensitive data (API keys, credentials)
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## Questions?

- **Issues**: [GitHub Issues](https://github.com/yourusername/enterprise-rag-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/enterprise-rag-system/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎉
