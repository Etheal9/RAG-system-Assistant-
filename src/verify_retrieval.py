import os
import sys
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # 1. Setup Data
    print("--- 1. Loading Data ---")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    # Target specific file mentioned in prompt or all
    file_path = os.path.join(data_dir, "Enterprise RAG System .md")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

    print(f"Loading {file_path}...")
    raw_docs = loader.load_file(file_path)
    print(f"Loaded {len(raw_docs)} document(s).")
    
    print("Cleaning...")
    for doc in raw_docs:
        doc.page_content = cleaner.clean(doc.page_content)
        
    print("Splitting...")
    chunks = splitter.split_documents(raw_docs)
    print(f"Created {len(chunks)} chunks.")
    
    # 2. Setup Vector Store
    print("\n--- 2. Building Vector Index ---")
    try:
        embedding_model = EmbeddingModel()
        manager = VectorStoreManager(embedding_model)
        manager.create_index(chunks)
        print("Index created successfully.")
    except Exception as e:
        print(f"Error creating index (likely missing API Key): {e}")
        return

    # 3. Retrieval
    print("\n--- 3. Verifying Retrieval ---")
    retriever = Retriever(manager)
    
    queries = [
        "What is the system prompt structure?",
        "How is chunking handled?",
        "Does the system allow hallucinations?"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        response = retriever.retrieve_with_logs(q, k=3)
        
        print("Retrieved Results:")
        for log in response['logs']:
            print(f"  [{log['rank']}] Score: {log['score']:.4f} | Source: {log['source']}")
            print(f"      Snippet: {log['content_snippet']}")
            
if __name__ == "__main__":
    main()
