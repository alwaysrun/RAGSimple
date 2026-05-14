# RAGSimple Usage Guide

This guide explains how to install, configure, and use RAGSimple.

---

## Prerequisites

- Python 3.11+
- micromamba or conda (recommended)
- API key for LLM service (DashScope)

---

## Installation

### 1. Activate Python Environment

```powershell
micromamba activate ai_py3.11
```

### 2. Install Dependencies

```powershell
cd RAGSimple
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `configures/` directory:

```powershell
New-Item -Path "configures\.env" -ItemType "file" -Force
```

Add your API key:

```env
DASHSCOPE_API_KEY=your_api_key_here
```

---

## Configuration

Edit `configures/config.toml` to customize settings:

### Backend Settings

```toml
[backend]
host = "0.0.0.0"    # API host
port = 8000         # API port
db_path = "data/DB" # Vector database path
```

### RAG Settings

```toml
[rag]
chunk_size = 1000           # Document chunk size
chunk_overlap = 200         # Overlap between chunks
semantic_threshold = 0.5    # Semantic chunking threshold
```

### Model Settings

```toml
[models]
llm_type = "openai"
llm_model = "glm-5"
llm_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
embedding_type = "huggingface"
embedding_model = "BAAI/bge-small-zh-v1.5"
```

---

## Running the Application

### Start Backend

```powershell
python main.py backend
```

Output:
```
🚀 Starting RAGSimple Backend...
📍 Host: 0.0.0.0
📍 Port: 8000
📍 Config: glm-5 / BAAI/bge-small-zh-v1.5
```

### Start Frontend

In a new terminal:

```powershell
python main.py frontend
```

Output:
```
🎨 Starting RAGSimple Frontend...
```

The Streamlit UI will open in your browser at `http://localhost:8501`.

---

## Using the Web Interface

### 1. Upload Documents

1. Open the Streamlit UI in your browser
2. In the sidebar, click **"Upload Documents"**
3. Select files (PDF, TXT, or MD)
4. Click **"🚀 Ingest Documents"**
5. Wait for indexing to complete

### 2. Query Documents

1. In the main chat area, type your question
2. Press Enter to submit
3. The answer will appear with source citations
4. Click **"Sources"** to expand and view source documents

### 3. Reset Database

1. In the sidebar, click **"🗑️ Reset Database"**
2. Confirm the action
3. All indexed documents will be removed

---

## Using the API Directly

### Python Client

```python
from app.frontend.api_client import RAGClient

client = RAGClient("http://localhost:8000")

# Check configuration
config = client.get_config()
print(f"Using LLM: {config['llm_model']}")

# Ingest documents
with open("document.pdf", "rb") as f:
    files = [("document.pdf", f.read())]
    result = client.ingest(files)
    print(f"Indexed: {result['indexed_files']}")

# Query
response = client.query("What is the main topic?")
print(f"Answer: {response['answer']}")
for source in response['sources']:
    print(f"Source: {source['metadata']['source']}")

# Reset when done
client.reset()
```

### cURL Examples

**Ingest:**
```bash
curl -X POST "http://localhost:8000/ingest" \
     -F "files=@document.pdf"
```

**Query:**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is this about?"}'
```

**Get Config:**
```bash
curl -X GET "http://localhost:8000/config"
```

**Reset:**
```bash
curl -X DELETE "http://localhost:8000/reset"
```

---

## Supported File Types

| Extension | Format | Notes |
|-----------|--------|-------|
| `.pdf` | PDF | Text extracted using pypdf |
| `.txt` | Plain Text | UTF-8 encoded |
| `.md` | Markdown | UTF-8 encoded |

---

## Troubleshooting

### Backend Won't Start

**Error:** `DASHSCOPE_API_KEY not found in environment`

**Solution:** Ensure `.env` file exists in `configures/` directory with valid API key:
```env
DASHSCOPE_API_KEY=sk-your-key-here
```

### Embedding Model Download

**First run:** The HuggingFace embedding model will be downloaded automatically. This may take a few minutes.

**Location:** Models are cached in `~/.cache/huggingface/`

### Connection Refused

**Error:** `Could not connect to Backend`

**Solution:**
1. Ensure backend is running: `python main.py backend`
2. Check the port is not in use
3. Verify `BACKEND_URL` environment variable if customized

### PDF Extraction Issues

**Problem:** PDF text not extracted correctly

**Solution:**
- Ensure PDF contains selectable text (not scanned images)
- For scanned PDFs, consider adding OCR support

---

## Running Tests

```powershell
pytest tests/
```

Test coverage includes:
- Configuration loading
- Model factory
- Document ingestion
- RAG service operations

---

## Advanced Usage

### Custom Embedding Model

Edit `config.toml`:
```toml
[models]
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
```

### Custom LLM

For OpenAI:
```toml
[models]
llm_type = "openai"
llm_model = "gpt-4"
llm_base_url = "https://api.openai.com/v1"
```

Add to `.env`:
```env
OPENAI_API_KEY=your_openai_key
```

### Change Chunk Sizes

Adjust for your document type:
```toml
[rag]
chunk_size = 2000      # Larger for comprehensive context
chunk_overlap = 400    # More overlap for better continuity
```

---

## API Documentation

When the backend is running, access interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
