# RAGSimple

A modular Retrieval-Augmented Generation (RAG) system with a clean, decoupled architecture for local document search and AI-powered chat.

## Overview

RAGSimple combines **FastAPI** backend with **Streamlit** frontend to deliver a production-ready RAG solution. It leverages LangChain for RAG orchestration, ChromaDB for vector storage, and supports multiple LLM providers through a flexible model factory pattern.

## Key Features

- **Parent-Child Indexing**: Small chunks (200-400 tokens) for precise retrieval, larger parent chunks (1000-2000 tokens) for rich context generation
- **Semantic Chunking**: Documents split based on meaning to maintain conceptual integrity
- **Local Embeddings**: Deploy efficient embedding models locally (`BGE-small-zh-v1.5` or `Qwen3-Embedding-0.6B`)
- **Multi-LLM Support**: Seamless switching between LLM providers via configuration (Ali-Bailian/DashScope with OpenAI-compatible API)
- **Persistent Storage**: ChromaDB vector store with local file-based document store

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│         (Document Upload, Chat Interface)                │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   RAGService │  │ModelFactory  │  │  Ingestion   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
│         │                 │                             │
│  ┌──────▼─────────────────▼──────────────────────────┐ │
│  │     ParentDocumentRetriever (LangChain)           │ │
│  └──────┬─────────────────┬──────────────────────────┘ │
│         │                 │                             │
│  ┌──────▼──────┐   ┌──────▼──────┐                     │
│  │  ChromaDB   │   │  DocStore   │                     │
│  │(Vector Store)│   │(File Store) │                     │
│  └─────────────┘   └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Micromamba (recommended) or conda

### Installation

```powershell
# Activate environment
micromamba activate ai_py3.11

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Edit `configures/config.toml` for non-sensitive settings (chunk sizes, model names, paths)
2. Create `configures/.env` for sensitive secrets (API keys):

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### Run the Application

```powershell
# Start backend (FastAPI)
python main.py --mode backend

# Start frontend (Streamlit) - in a new terminal
python main.py --mode frontend
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest` | Upload and index documents |
| POST | `/query` | Execute RAG query |
| GET | `/config` | Get active configuration |
| GET | `/documents` | List indexed documents |
| DELETE | `/reset` | Clear vector store |

## Project Structure

```
RAGSimple/
├── app/
│   ├── backend/          # FastAPI backend
│   │   ├── api/          # Routes and endpoints
│   │   ├── core/         # RAG logic, config, ingestion
│   │   └── models/       # ModelFactory, LLM wrappers
│   └── frontend/         # Streamlit frontend
├── configures/           # Configuration files
├── data/                 # ChromaDB and document storage
└── docs/                 # Design specifications
```

## Supported Document Types

- PDF (`.pdf`)
- Markdown (`.md`)
- Text (`.txt`)
