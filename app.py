import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.ingestion import DocumentLoader, TextCleaner, TextSplitter
from src.vectorizer import EmbeddingModel, VectorStoreManager
from src.retrieval import Retriever
from src.rag import RAGChain

# Page config
st.set_page_config(
    page_title="Docmentation Assistance for RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        max-width: 80%;
    }
    .source-box {
        background: #e8eaf6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #667eea;
        color: #1a1a1a;
    }
    .source-box strong {
        color: #667eea;
    }
    .source-box em {
        color: #424242;
    }
    h1 {
        color: black;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system (cached to avoid reloading)"""
    load_dotenv()
    
    with st.spinner("🔄 Loading documents and building index..."):
        loader = DocumentLoader()
        cleaner = TextCleaner()
        splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
        
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Automatically load ALL markdown files from data directory
        all_chunks = []
        loaded_files = []
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.md') or filename.endswith(',md'):
                file_path = os.path.join(data_dir, filename)
                try:
                    raw_docs = loader.load_file(file_path)
                    for doc in raw_docs:
                        doc.page_content = cleaner.clean(doc.page_content)
                    file_chunks = splitter.split_documents(raw_docs)
                    all_chunks.extend(file_chunks)
                    loaded_files.append(filename)
                except Exception as e:
                    st.warning(f"⚠️ Could not load {filename}: {str(e)}")
        
        if not all_chunks:
            raise Exception("No documents found in data/ folder!")
        
        embedding_model = EmbeddingModel()
        manager = VectorStoreManager(embedding_model)
        manager.create_index(all_chunks)
        
        retriever = Retriever(vector_store_manager=manager)
        
        # Store loaded files in session state for display
        st.session_state.loaded_files = loaded_files
        st.session_state.total_chunks = len(all_chunks)
        
        return RAGChain(retriever=retriever)

def main():
    # Header
    st.title("🤖 ASk About Your Documents")
    st.markdown("### Ask questions about your documents")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 System Info")
        st.info("""
        **Powered by:**
        - 🧠 Groq (Llama 3.3 70B)
        - 🔍 HuggingFace Embeddings
        - 📊 FAISS Vector Store
        """)
        
        st.header("📖 Loaded Documents")
        if "loaded_files" in st.session_state:
            st.success(f"**{len(st.session_state.loaded_files)} documents loaded**")
            st.info(f"**Total chunks:** {st.session_state.total_chunks}")
            with st.expander("View all files"):
                for file in st.session_state.loaded_files:
                    st.write(f"✓ {file}")
        else:
            st.info("Loading documents...")
        
        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize RAG system
    try:
        rag_chain = initialize_rag_system()
        st.success("✅ System Ready!")
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        return
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📄 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>Source {i}:</strong> {source['source']}<br>
                            <em>{source['content'][:200]}...</em>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about the documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    result = rag_chain.answer(prompt)
                    answer = result["answer"]
                    sources = result["source_documents"]
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Display sources
                    if sources:
                        with st.expander("📄 View Sources"):
                            for i, doc in enumerate(sources, 1):
                                source_name = doc.metadata.get('source', 'Unknown')
                                st.markdown(f"""
                                <div class="source-box">
                                    <strong>Source {i}:</strong> {source_name}<br>
                                    <em>{doc.page_content[:200]}...</em>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Save to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": [
                            {
                                "source": doc.metadata.get('source', 'Unknown'),
                                "content": doc.page_content
                            }
                            for doc in sources
                        ]
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

if __name__ == "__main__":
    main()
