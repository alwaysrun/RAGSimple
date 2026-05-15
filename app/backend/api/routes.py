print("🛣️  Setting up API routes...")
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.backend.core.rag_service import RAGService
from app.backend.core.config import settings
from langchain_core.documents import Document
import io
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
rag_service = RAGService()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@router.post("/ingest", response_model=Dict[str, Any])
async def ingest_files(files: List[UploadFile] = File(...)):
    try:
        docs = []
        for file in files:
            content = await file.read()
            # Simple text/pdf handling (could be expanded with proper loaders)
            if file.filename.endswith(".txt") or file.filename.endswith(".md"):
                text = content.decode("utf-8")
                docs.append(Document(page_content=text, metadata={"source": file.filename}))
            elif file.filename.endswith(".pdf"):
                try:
                    import pypdf
                    pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
                    docs.append(Document(page_content=text, metadata={"source": file.filename}))
                except Exception as pdf_err:
                    logger.error(f"Error parsing PDF {file.filename}: {pdf_err}")
                    logger.error(traceback.format_exc())
                    raise HTTPException(status_code=400, detail=f"Error parsing PDF {file.filename}: {str(pdf_err)}")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        if not docs:
            raise HTTPException(status_code=400, detail="No extractable text found in the provided files.")
            
        rag_service.ingest(docs)
        return {"status": "success", "indexed_files": [f.filename for f in files]}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        result = rag_service.query(request.query)
        answer = result.get("result", result.get("answer", "")) # RetrievalQA uses 'result'
        sources = [
            {"content": doc.page_content[:200] + "...", "metadata": doc.metadata}
            for doc in result.get("source_documents", [])
        ]
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config():
    return {
        "llm_model": settings.models.llm_model,
        "embedding_model": settings.models.embedding_model,
        "db_path": settings.backend.db_path
    }

@router.delete("/reset")
async def reset_db():
    try:
        rag_service.reset()
        return {"status": "success", "message": "Vector store reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
