import os
import sys
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

def main():
    load_dotenv()
    
    print("=== Enterprise RAG System Initialization ===")
    
    # 1. Ingestion
    print("--> Loading Documents...")
    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    # In a real system we might scan the dir, here we load specific key files
    files_to_load = [
        "Enterprise RAG System .md",
        "Docling.md",
        "The Science of Chunking,md"
    ]
    
    all_chunks = []
    
    for filename in files_to_load:
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            print(f"    Processing: {filename}")
            raw_docs = loader.load_file(file_path)
            # Clean
            for doc in raw_docs:
                doc.page_content = cleaner.clean(doc.page_content)
            # Split
            file_chunks = splitter.split_documents(raw_docs)
            all_chunks.extend(file_chunks)
        else:
            print(f"    WARNING: File not found {filename}")

    print(f"--> Total Chunks Created: {len(all_chunks)}")
    
    # 2. Vector Store
    print("--> Building Vector Index...")
    try:
        embedding_model = EmbeddingModel()
        manager = VectorStoreManager(embedding_model)
        manager.create_index(all_chunks)
    except Exception as e:
        print(f"FATAL ERROR: Could not create index. Check API Keys. Details: {e}")
        return

    # 3. RAG Chain
    retriever = Retriever(vector_store_manager=manager)
    rag_chain = RAGChain(retriever=retriever)
    
    print("\n=== System Ready! (Type 'exit' to quit) ===\n")
    
    while True:
        query = input("\nEnter your question: ")
        if query.lower() in ['exit', 'quit']:
            break
            
        if not query.strip():
            continue
            
        print("\nProcessing...")
        result = rag_chain.answer(query)
        
        print(f"\n>> ANSWER:\n{result['answer']}\n")
        print("\n>> SOURCES:")
        for doc in result['source_documents']:
            source = doc.metadata.get('source', 'unknown')
            print(f"   - {os.path.basename(source)}")

if __name__ == "__main__":
    main()
