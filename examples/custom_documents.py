"""
Example: Using custom documents with the RAG system.

This script shows how to:
1. Add your own documents programmatically
2. Process them into the system
3. Query against your custom knowledge base
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

def main():
    load_dotenv()
    
    print("=== Custom Documents Example ===\n")
    
    # Initialize
    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    
    # Option 1: Load from specific file
    print("Loading custom document...")
    custom_file = "data/Enterprise RAG System .md"  # Replace with your file
    
    docs = loader.load_file(custom_file)
    for doc in docs:
        doc.page_content = cleaner.clean(doc.page_content)
    
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks from {custom_file}\n")
    
    # Create index
    embedding_model = EmbeddingModel()
    manager = VectorStoreManager(embedding_model)
    manager.create_index(chunks)
    
    # Create RAG chain
    retriever = Retriever(vector_store_manager=manager)
    rag_chain = RAGChain(retriever=retriever)
    
    # Ask questions about your custom document
    question = "What does this document discuss?"
    print(f"Question: {question}")
    result = rag_chain.answer(question)
    print(f"Answer: {result['answer']}\n")

if __name__ == "__main__":
    main()
