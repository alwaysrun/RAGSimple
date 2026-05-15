import streamlit as st
from app.frontend.api_client import RAGClient
import os

# Initialize API Client
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
client = RAGClient(BACKEND_URL)

st.set_page_config(page_title="RAGSimple", layout="wide")

# Sidebar
with st.sidebar:
    st.title("⚙️ RAGSimple Control")
    
    try:
        config = client.get_config()
        st.info(f"**LLM:** {config['llm_model']}\n\n**Embeddings:** {config['embedding_model']}")
    except Exception:
        st.error("Could not connect to Backend.")

    st.divider()
    
    st.subheader("📁 Document Management")
    uploaded_files = st.file_uploader("Upload Documents", type=["pdf", "txt", "md"], accept_multiple_files=True)
    
    if st.button("🚀 Ingest Documents") and uploaded_files:
        with st.spinner("Indexing..."):
            try:
                files_to_send = [(f.name, f.getvalue()) for f in uploaded_files]
                result = client.ingest(files_to_send)
                st.success(f"Indexed {len(result['indexed_files'])} files.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

    st.divider()
    
    if st.button("🗑️ Reset Database"):
        if st.confirm("Are you sure you want to clear the vector store?"):
            try:
                client.reset()
                st.success("Database cleared.")
            except Exception as e:
                st.error(f"Reset failed: {e}")

# Main Chat Area
st.title("💬 RAGSimple Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source['metadata'].get('source', 'Unknown')}: {source['content']}")

# Chat input
if prompt := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.query(prompt)
                answer = response["answer"]
                sources = response["sources"]
                
                st.markdown(answer)
                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.write(f"- {source['metadata'].get('source', 'Unknown')}: {source['content']}")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer, 
                    "sources": sources
                })
            except Exception as e:
                st.error(f"Query failed: {e}")

# if __name__ == "__main__":
#     # This allows the script to be run directly via 'python app/frontend/main.py'
#     # but still works with 'streamlit run app/frontend/main.py'
#     import subprocess
#     import sys
    
#     # Get the absolute path of the current file
#     file_path = os.path.abspath(__file__)
#     # Run streamlit
#     subprocess.run([sys.executable, "-m", "streamlit", "run", file_path])
