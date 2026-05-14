# RAGSimple Design: Backend & Advanced RAG

## 1. Core Components (FastAPI)

### Advanced Ingestion Pipeline
- **Document Loaders:** `.pdf`, `.md`, `.txt` support.
- **Chunking Strategy:**
    - **Semantic Chunking:** Splitting text based on semantic meaning to keep related concepts together.
    - **Parent-Child Indexing:** Using `ParentDocumentRetriever`. 
        - **Child Chunks:** Smaller segments for semantic search.
        - **Parent Chunks:** Full context retrieved for the LLM.
- **Vector Store:** `Chroma` persisted at `{output_dir}/Data/DB`.

### Model & Embedding Layer
- **LLM Provider:** Ali-Bailian (DashScope) using its **OpenAI-compatible API** (e.g., via `ChatOpenAI` in LangChain).
- **Embedding Provider:** **Locally deployed** model.
    - Options: `BGE-small-zh-v1.5` or `Qwen3-Embedding-0.6B`.
    - Implementation: Using `HuggingFaceEmbeddings` (local) or a local inference server like Ollama/vLLM if preferred.
- **Abstraction:** `ModelFactory` to handle API base URLs and local model paths.

### Configuration Management
- **`config.toml`:** Non-sensitive settings (API base URLs, local model names/paths, chunking parameters, DB location).
- **`.env`:** `DASHSCOPE_API_KEY` and other sensitive credentials.

## 2. API Endpoints

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/ingest` | Uploads, chunks (Parent-Child), and indexes files. | `Multipart/form-data` |
| `POST` | `/query` | Executes RAG query using Parent context. | `{"query": "string"}` |
| `GET` | `/config` | Returns current active configuration. | N/A |
| `DELETE` | `/reset` | Clears `{output_dir}/Data/DB`. | N/A |

---
**Does this updated integration strategy (OpenAI-compatible for LLM, Local for Embeddings) look correct?** If so, I'll proceed to detail the **Streamlit Frontend**.
