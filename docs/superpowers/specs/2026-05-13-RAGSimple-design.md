# RAGSimple Design Specification

**Date:** 2026-05-13
**Status:** Draft for Review

## 1. Project Overview
RAGSimple is a modular Retrieval-Augmented Generation (RAG) system designed to provide a clean, decoupled architecture for local document search and chat. It features a FastAPI backend for core RAG logic and a Streamlit frontend for user interaction.

## 2. System Architecture

### 2.1 Backend (FastAPI)
- **Framework:** FastAPI for high-performance REST API endpoints.
- **RAG Orchestration:** LangChain for managing the "Retrieve-then-Generate" flow.
- **Vector Store:** ChromaDB, persisted locally at `{output}/Data/DB`.
- **Configuration:** 
    - `configures/config.toml`: Non-sensitive settings (chunk sizes, model names, paths).
    - `configures/.env`: Sensitive secrets (API keys).

### 2.2 Advanced RAG Features
- **Semantic Chunking:** Splitting documents based on meaning to maintain conceptual integrity.
- **Parent-Child Indexing:** 
    - **Child Chunks:** Small segments (200-400 tokens) for precise semantic matching.
    - **Parent Chunks:** Larger context (1000-2000 tokens) retrieved and passed to the LLM for generation.

### 2.3 Model & Embedding Strategy
- **LLM:** Ali-Bailian (DashScope) accessed via **OpenAI-compatible API**.
- **Embeddings:** **Locally deployed** efficient models (`BGE-small-zh-v1.5` or `Qwen3-Embedding-0.6B`).
- **Integration:** `ModelFactory` abstraction to support multiple LLM providers.

### 2.4 Frontend (Streamlit)
- **Sidebar:** Document uploading, ingestion trigger, document listing, and database reset.
- **Chat Interface:** Standard chat bubbles with optional source reference expanders.
- **Communication:** Uses a dedicated Python API client to communicate with the FastAPI service via HTTP.

## 3. API Endpoints

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/ingest` | Uploads, chunks (Semantic + Parent-Child), and indexes files. | `Multipart/form-data` |
| `POST` | `/query` | Executes RAG query using Parent context. | `{"query": "string"}` |
| `GET` | `/config` | Returns active non-sensitive configuration. | N/A |
| `GET` | `/documents`| Lists currently indexed document metadata. | N/A |
| `DELETE` | `/reset` | Clears the vector store and indexed files. | N/A |

## 4. Directory Structure
```text
RAGSimple/
├── app/
│   ├── backend/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # RAG logic, loaders, splitters
│   │   └── models/       # ModelFactory and LLM wrappers
│   └── frontend/
│       ├── main.py       # Streamlit entry point
│       └── api_client.py # Client for backend API
├── configures/
│   ├── config.toml       # Public settings
│   └── .env              # Private secrets
├── data/
│   └── DB/               # ChromaDB persistence (configured via TOML)
├── docs/
│   └── superpowers/      # Design specs and plans
└── ...
```

## 5. Success Criteria
1. Successfully ingest PDF/MD/TXT files with Semantic Chunking.
2. Accurate retrieval using Parent-Child indexing.
3. Stable chat interaction via Streamlit through the FastAPI backend.
4. Seamless switching of LLMs via configuration.
