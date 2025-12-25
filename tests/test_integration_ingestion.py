import pytest
from src.ingestion import DocumentLoader, TextCleaner, TextSplitter

def test_full_ingestion_pipeline(tmp_path):
    # 1. Setup: Create a dummy markdown file
    file_content = "# Title\n\n  This is a   test document.  \n\nIt has multiple paragraphs."
    file_path = tmp_path / "integration_test.md"
    file_path.write_text(file_content, encoding="utf-8")

    # 2. components
    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)

    # 3. Execution Flow
    # Step A: Load
    raw_docs = loader.load_file(str(file_path))
    assert len(raw_docs) == 1
    
    # Step B: Clean (Apply cleaning to page_content)
    # Note: In a real pipeline this might be inside a loop or mapped
    cleaned_content = cleaner.clean(raw_docs[0].page_content)
    raw_docs[0].page_content = cleaned_content
    
    # Check cleaning effect
    assert "This is a test document." in cleaned_content
    assert "  " not in cleaned_content

    # Step C: Split
    chunks = splitter.split_documents(raw_docs)

    # 4. Verification
    assert len(chunks) >= 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 50
        assert chunk.metadata["source"] == str(file_path)
