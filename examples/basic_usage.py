"""
Basic usage example for the Enterprise RAG System.

This script demonstrates how to:
1. Load and process documents
2. Create a vector index
3. Ask questions and get answers
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

def main():
    # Load environment variables
    load_dotenv()
    
    print("=== Enterprise RAG System - Basic Usage ===\n")
    
    # Step 1: Initialize components
    print("1. Initializing components...")
    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    
    # Step 2: Load documents
    print("2. Loading documents...")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    all_chunks = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(data_dir, filename)
            print(f"   - Loading: {filename}")
            
            # Load and clean
            raw_docs = loader.load_file(file_path)
            for doc in raw_docs:
                doc.page_content = cleaner.clean(doc.page_content)
            
            # Split into chunks
            chunks = splitter.split_documents(raw_docs)
            all_chunks.extend(chunks)
    
    print(f"   Total chunks: {len(all_chunks)}")
    
    # Step 3: Create vector index
    print("3. Creating vector index...")
    embedding_model = EmbeddingModel()
    manager = VectorStoreManager(embedding_model)
    manager.create_index(all_chunks)
    print("   Index created!")
    
    # Step 4: Create RAG chain
    print("4. Creating RAG chain...")
    retriever = Retriever(vector_store_manager=manager)
    rag_chain = RAGChain(retriever=retriever)
    print("   RAG chain ready!")
    
    # Step 5: Ask questions
    print("\n=== Asking Questions ===\n")
    
    questions = [
        "What is RAG?",
        "How does chunking work?",
        "What are best practices for RAG systems?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        result = rag_chain.answer(question)
        print(f"Answer: {result['answer']}\n")
        print(f"Sources: {len(result['source_documents'])} documents\n")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    main()
