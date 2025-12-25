from langchain_core.prompts import ChatPromptTemplate

# Strict System Prompt
# Enforces:
# 1. Grounding (Use ONLY provided context)
# 2. Refusal (Say "I don't know" if context is missing)
# 3. Citation (Cite sources if possible - implied by sticking to context)

RAG_SYSTEM_PROMPT = """You are a rag system document assistance that answers questions based on the provided context.
You will be provided with a set of retrieved document chunks (Context).
You must answer the user's question using ONLY the provided Context.

Rules:
1. Do NOT use your internal knowledge to answer the question.
2. If the answer is not present in the Context, you MUST respond with EXACTLY this phrase and nothing else: "I don't know based on the provided documents."
3. Do not make up or hallucinate information.
4. Keep your answer concise and directly related to the question.

Context:
{context}
"""

def get_rag_prompt_template() -> ChatPromptTemplate:
    """Returns the chat prompt template for the RAG chain."""
    return ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
