# RAGSimple Backend API Reference

This document provides a comprehensive reference for the RAGSimple Backend REST API.

## Base URL

```
http://localhost:8000
```

The base URL can be configured via `configures/config.toml` under the `[backend]` section.

---

## Endpoints

### 1. Ingest Documents

Upload and index documents into the vector store.

**Endpoint:** `POST /ingest`

**Content-Type:** `multipart/form-data`

**Request:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | `List[UploadFile]` | Yes | List of files to ingest |

**Supported File Types:**
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents

**Response:**
```json
{
    "status": "success",
    "indexed_files": ["document1.pdf", "document2.txt"]
}
```

**Error Response:**
```json
{
    "detail": "Unsupported file type: document.docx"
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/ingest" \
     -F "files=@document1.pdf" \
     -F "files=@document2.txt"
```

**Example (Python):**
```python
import requests

files = [
    ("files", ("document.pdf", open("document.pdf", "rb"))),
    ("files", ("notes.txt", open("notes.txt", "rb")))
]
response = requests.post("http://localhost:8000/ingest", files=files)
print(response.json())
```

---

### 2. Query

Execute a RAG query against the indexed documents.

**Endpoint:** `POST /query`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "query": "What is the main topic of the documents?"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `string` | Yes | The question to ask |

**Response:**
```json
{
    "answer": "The main topic is about...",
    "sources": [
        {
            "content": "Relevant text chunk from document...",
            "metadata": {
                "source": "document1.pdf"
            }
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `answer` | `string` | The generated answer from the LLM |
| `sources` | `List[Dict]` | List of source documents used for the answer |
| `sources[].content` | `string` | Preview of the source content (truncated to 200 chars) |
| `sources[].metadata` | `Dict` | Metadata including the source filename |

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the key points?"}'
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What are the key points?"}
)
result = response.json()
print(f"Answer: {result['answer']}")
for source in result['sources']:
    print(f"Source: {source['metadata']['source']}")
```

---

### 3. Get Configuration

Retrieve the current backend configuration.

**Endpoint:** `GET /config`

**Response:**
```json
{
    "llm_model": "glm-5",
    "embedding_model": "BAAI/bge-small-zh-v1.5",
    "db_path": "data/DB"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `llm_model` | `string` | The LLM model being used |
| `embedding_model` | `string` | The embedding model being used |
| `db_path` | `string` | Path to the vector database |

**Example (cURL):**
```bash
curl -X GET "http://localhost:8000/config"
```

---

### 4. Reset Database

Clear all indexed documents from the vector store.

**Endpoint:** `DELETE /reset`

**Response:**
```json
{
    "status": "success",
    "message": "Vector store reset"
}
```

**Warning:** This operation is irreversible and will delete all indexed documents.

**Example (cURL):**
```bash
curl -X DELETE "http://localhost:8000/reset"
```

---

## Error Handling

All endpoints return standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `400` | Bad Request (e.g., unsupported file type) |
| `500` | Internal Server Error |

Error responses include a `detail` field with the error message:
```json
{
    "detail": "Error message describing the issue"
}
```

---

## API Client

A Python client is provided in `app/frontend/api_client.py`:

```python
from app.frontend.api_client import RAGClient

client = RAGClient("http://localhost:8000")

# Query
result = client.query("What is this document about?")
print(result["answer"])

# Ingest
files = [("doc.pdf", open("doc.pdf", "rb").read())]
result = client.ingest(files)

# Get config
config = client.get_config()

# Reset
client.reset()
```

---

## OpenAPI Documentation

Interactive API documentation is available when the backend is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
