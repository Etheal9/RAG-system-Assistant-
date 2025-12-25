from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from typing import List
import os

class DocumentLoader:
    def load_file(self, file_path: str) -> List[Document]:
        """
        Loads a markdown or text file and returns a list of Documents.
        
        Args:
            file_path (str): The absolute path to the file.
            
        Returns:
            List[Document]: A list containing the loaded document.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Basic text loading for now, can be enhanced with UnstructuredMarkdownLoader if needed
        # but standard TextLoader is safer for raw content control as per guidelines.
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            return loader.load()
        except Exception as e:
            # Fallback or specific handling could go here
            raise e

class TextCleaner:
    def clean(self, text: str) -> str:
        """
        Cleans the input text by:
        - Removing excessive whitespace
        - Standardizing newlines
        
        Args:
            text (str): The raw text to clean.
            
        Returns:
            str: The cleaned text.
        """
        if not text:
            return ""
        
        # Replace multiple newlines with a single newline to maintain paragraph structure but remove gaps
        # Or, typically for RAG, we might want to keep paragraph breaks (double newline).
        # Let's align with the test expectation: "This is a test.\nNew line." (single newline)
        
        import re
        # Replace multiple whitespace characters with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Replace multiple newlines with a single newline (as per test expectation)
        text = re.sub(r'\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        return text.strip()

from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextSplitter:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size (int): Check size in characters (approx tokens).
            chunk_overlap (int): Overlap size.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str) -> List[str]:
        """Splits text into chunks."""
        return self.splitter.split_text(text)
        
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Splits a list of documents into chunks."""
        return self.splitter.split_documents(documents)
