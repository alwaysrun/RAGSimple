# RAGSimple Architecture

This document describes the system architecture and main data flow of RAGSimple.

---

## System Overview

RAGSimple is a Retrieval-Augmented Generation (RAG) application built with a modular architecture. It enables users to upload documents, index them using vector embeddings, and query against the indexed content using an LLM.

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI]
        Client[API Client]
    end

    subgraph "Backend Layer"
        API[FastAPI Routes]
        Service[RAGService]
        Ingestion[Ingestion Module]
        Factory[Model Factory]
    end

    subgraph "Data Layer"
        VectorDB[(ChromaDB)]
        DocStore[(File DocStore)]
    end

    subgraph "External Services"
        LLM[LLM API<br/>DashScope/OpenAI]
        Embedding[Embedding Model<br/>HuggingFace]
    end

    UI --> Client
    Client --> API
    API --> Service
    Service --> Ingestion
    Service --> Factory
    Service --> VectorDB
    Service --> DocStore
    Factory --> LLM
    Factory --> Embedding
```

---

## Component Architecture

### 1. Frontend Layer

| Component | File | Description |
|-----------|------|-------------|
| **Streamlit UI** | `app/frontend/main.py` | Web-based user interface for document upload and querying |
| **API Client** | `app/frontend/api_client.py` | HTTP client for communicating with the backend API |

### 2. Backend Layer

| Component | File | Description |
|-----------|------|-------------|
| **FastAPI Routes** | `app/backend/api/routes.py` | REST API endpoints |
| **FastAPI App** | `app/backend/api/main.py` | FastAPI application configuration |
| **RAGService** | `app/backend/core/rag_service.py` | Core RAG orchestration service |
| **Ingestion** | `app/backend/core/ingestion.py` | Document processing and chunking |
| **Config** | `app/backend/core/config.py` | Configuration management |
| **Model Factory** | `app/backend/models/factory.py` | LLM and embedding model instantiation |

### 3. Data Layer

| Component | Type | Description |
|-----------|------|-------------|
| **ChromaDB** | Vector Database | Stores document embeddings for similarity search |
| **File DocStore** | Local File System | Stores parent document chunks for retrieval |

---

## Directory Structure

```
RAGSimple/
├── app/
│   ├── backend/
│   │   ├── api/           # REST API endpoints
│   │   │   ├── main.py    # FastAPI app
│   │   │   └── routes.py  # API routes
│   │   ├── core/          # Core business logic
│   │   │   ├── config.py      # Configuration
│   │   │   ├── ingestion.py   # Document processing
│   │   │   └── rag_service.py # RAG orchestration
│   │   └── models/
│   │       └── factory.py # Model creation
│   └── frontend/
│       ├── main.py        # Streamlit UI
│       └── api_client.py  # Backend client
├── configures/
│   └── config.toml        # Application configuration
├── data/
│   ├── DB/                # ChromaDB persistence
│   └── docstore/          # Parent document storage
├── docs/                  # Documentation
├── tests/                 # Test suite
└── main.py                # Entry point
```

---

## Main Data Flows

### Flow 1: Document Ingestion

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant Service as RAGService
    participant Retriever as ParentDocumentRetriever
    participant VectorDB as ChromaDB
    participant DocStore as File DocStore

    User->>UI: Upload files
    UI->>API: POST /ingest (files)
    API->>Service: ingest(docs)
    Service->>Retriever: add_documents(docs)
    
    Note over Retriever: Split into parent/child chunks
    
    Retriever->>VectorDB: Store child embeddings
    Retriever->>DocStore: Store parent documents
    Retriever-->>Service: Complete
    Service-->>API: Success
    API-->>UI: {"status": "success"}
    UI-->>User: Show confirmation
```

**Process Details:**
1. User uploads documents via Streamlit UI
2. Frontend sends files to `/ingest` endpoint
3. Backend converts files to LangChain `Document` objects
4. `ParentDocumentRetriever` splits documents:
   - **Parent chunks:** 2000 chars with 200 overlap
   - **Child chunks:** 400 chars with 50 overlap
5. Child chunks are embedded and stored in ChromaDB
6. Parent chunks are stored in File DocStore
7. Returns success status to user

---

### Flow 2: Query Execution

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant Service as RAGService
    participant Retriever as ParentDocumentRetriever
    participant VectorDB as ChromaDB
    participant DocStore as File DocStore
    participant LLM as LLM API

    User->>UI: Enter query
    UI->>API: POST /query (query)
    API->>Service: query(text)
    Service->>Retriever: retrieve(query)
    
    Note over Retriever: Embed query
    
    Retriever->>VectorDB: Similarity search (child chunks)
    VectorDB-->>Retriever: Matching child IDs
    Retriever->>DocStore: Get parent documents
    DocStore-->>Retriever: Parent documents
    
    Note over Retriever: Return full parent context
    
    Retriever-->>Service: Relevant documents
    Service->>LLM: Generate answer with context
    LLM-->>Service: Answer
    Service-->>API: {answer, sources}
    API-->>UI: Response
    UI-->>User: Display answer + sources
```

**Process Details:**
1. User submits a question via Streamlit UI
2. Frontend sends query to `/query` endpoint
3. Query is embedded using the embedding model
4. ChromaDB performs similarity search on child chunks
5. Parent documents are retrieved from File DocStore
6. LLM generates answer using parent document context
7. Returns answer and source documents to user

---

## Parent-Child Retrieval Strategy

RAGSimple uses a **Parent-Child Retrieval** strategy for improved context quality:

```mermaid
graph LR
    subgraph "Indexing"
        Doc[Document] --> Parent[Parent Chunk<br/>2000 chars]
        Doc --> Parent2[Parent Chunk]
        Parent --> Child1[Child Chunk<br/>400 chars]
        Parent --> Child2[Child Chunk]
        Parent2 --> Child3[Child Chunk]
    end

    subgraph "Retrieval"
        Query[Query] --> Search[Similarity Search]
        Search --> Match[Matched Child]
        Match --> Retrieve[Retrieve Parent]
    end
```

**Benefits:**
- **Small chunks for search:** Better semantic matching
- **Large chunks for context:** More complete information for LLM
- **Reduced fragmentation:** Answers have full context

---

## Configuration

Configuration is managed via `configures/config.toml`:

```toml
[backend]
host = "0.0.0.0"
port = 8000
db_path = "data/DB"

[rag]
chunk_size = 1000
chunk_overlap = 200
semantic_threshold = 0.5

[models]
llm_type = "openai"
llm_model = "glm-5"
llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
embedding_type = "huggingface"
embedding_model = "BAAI/bge-small-zh-v1.5"
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Framework** | FastAPI | REST API backend |
| **UI Framework** | Streamlit | Web-based frontend |
| **RAG Framework** | LangChain | RAG pipeline orchestration |
| **Vector DB** | ChromaDB | Embedding storage and retrieval |
| **LLM** | DashScope/OpenAI-compatible | Answer generation |
| **Embeddings** | HuggingFace | Local embedding model |
| **Config** | TOML + Pydantic | Configuration management |

---

## Key Design Decisions

1. **Separation of Concerns:** Clear separation between API, core logic, and data layers
2. **Factory Pattern:** `ModelFactory` for flexible model instantiation
3. **Parent-Child Retrieval:** Optimized for both search accuracy and context completeness
4. **Local Embeddings:** HuggingFace models for offline embedding generation
5. **Configurable:** All parameters externalized to TOML configuration
