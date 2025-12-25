import json
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

def setup_rag_system():
    """Initializes the RAG system by loading data and building the index."""
    print("--> Initializing System for Evaluation...")
    loader = DocumentLoader()
    cleaner = TextCleaner()
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    files_to_load = [
        "Enterprise RAG System .md",
        "Docling.md",
        "The Science of Chunking,md"
    ]
    
    all_chunks = []
    for filename in files_to_load:
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            raw_docs = loader.load_file(file_path)
            for doc in raw_docs:
                doc.page_content = cleaner.clean(doc.page_content)
            file_chunks = splitter.split_documents(raw_docs)
            all_chunks.extend(file_chunks)
            
    embedding_model = EmbeddingModel()
    manager = VectorStoreManager(embedding_model)
    manager.create_index(all_chunks)
    
    retriever = Retriever(vector_store_manager=manager)
    return RAGChain(retriever=retriever)

def evaluate():
    load_dotenv()
    rag_chain = setup_rag_system()
    
    eval_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'eval_set.json')
    with open(eval_file, 'r') as f:
        test_cases = json.load(f)
        
    print(f"\n=== RUNNING EVALUATION ON {len(test_cases)} CASES ===\n")
    
    passed_refusals = 0
    total_refusals = 0
    
    output_lines = []
    
    for i, case in enumerate(test_cases):
        question = case['question']
        expected = case['ground_truth']
        type_ = case['type']
        
        output_lines.append(f"[{i+1}/{len(test_cases)}] Type: {type_}")
        output_lines.append(f"Q: {question}")
        
        try:
            result = rag_chain.answer(question)
            answer = result['answer']
        except Exception as e:
            answer = f"ERROR: {str(e)}"
        
        output_lines.append(f"A: {answer}")
        output_lines.append(f"Expected: {expected}")
        
        # Grading Logic
        valid = "REVIEW REQUIRED"
        if type_ == 'refusal':
            total_refusals += 1
            # Check for standard refusal phrase
            if "I don't know" in answer or "not present" in answer:
                valid = "PASS"
                passed_refusals += 1
            else:
                valid = "FAIL"
        
        output_lines.append(f"Result: {valid}")
        output_lines.append("-" * 50)
        
    output_lines.append("\n=== SUMMARY ===")
    if total_refusals > 0:
        output_lines.append(f"Refusal Accuracy: {passed_refusals}/{total_refusals} ({passed_refusals/total_refusals*100:.1f}%)")
    else:
        output_lines.append("No refusal cases found.")
        
    output_lines.append("Specific answers require manual or LLM-based verification.")
    
    full_output = "\n".join(output_lines)
    print(full_output)
    
    with open("eval_output.txt", "w", encoding="utf-8") as f:
        f.write(full_output)

if __name__ == "__main__":
    evaluate()
