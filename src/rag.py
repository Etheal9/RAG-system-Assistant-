from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from src.retrieval import Retriever
from src.prompts import get_rag_prompt_template

class RAGChain:
    def __init__(self, retriever: Retriever, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialize the RAG Chain.
        
        Args:
            retriever (Retriever): The retrieval engine.
            model_name (str): LLM model name.
        """
        self.retriever = retriever
        # Uses GROQ_API_KEY from environment
        self.llm = ChatGroq(model=model_name, temperature=0)
        self.prompt_template = get_rag_prompt_template()

    def answer(self, query: str) -> Dict[str, Any]:
        """
        Answer a user query using RAG.
        
        Args:
            query (str): User question.
            
        Returns:
            dict: {
                "answer": str,
                "source_documents": List[Document],
                "query": str
            }
        """
        # 1. Retrieve
        docs = self.retriever.retrieve(query)
        
        # 2. Format Context
        context_text = "\n\n".join([d.page_content for d in docs])
        
        # 3. Prepare Prompt
        messages = self.prompt_template.invoke({
            "context": context_text,
            "question": query
        })
        
        # LOGGING (Observability)
        # In a real app we'd use a logger, here we print or store for inspection as per reqs
        print("\n--- [OBSERVABILITY] FINAL PROMPT SENT TO LLM ---")
        for m in messages.to_messages():
            print(f"[{m.type.upper()}]: {m.content}")
        print("--------------------------------------------------\n")
        
        # 4. Generate
        response = self.llm.invoke(messages)
        
        # Handle Gemini parsed content (sometimes list of dicts)
        content_text = response.content
        if isinstance(content_text, list):
            # Extract text from blocks like [{'type': 'text', 'text': '...'}]
            content_text = "".join([
                item.get('text', '') for item in content_text 
                if isinstance(item, dict) and item.get('type') == 'text'
            ])
        elif not isinstance(content_text, str):
            content_text = str(content_text)

        print("\n--- [OBSERVABILITY] RAW MODEL RESPONSE ---")
        print(response.content) # Keep raw for debugging
        print("------------------------------------------\n")
        
        return {
            "answer": content_text,
            "source_documents": docs,
            "query": query,
            "generated_prompt": messages # Store if we want to return it programmatically
        }
