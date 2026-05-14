import pytest
from langchain_core.documents import Document
from app.backend.core.rag_service import RAGService

@pytest.fixture
def rag_service():
    return RAGService()

def test_rag_service_ingest_and_query(rag_service):
    # Test ingestion
    docs = [Document(page_content="The capital of France is Paris. It is a beautiful city.")]
    rag_service.ingest(docs)
    
    # Test query
    # Note: We need a valid API key for the LLM to work, 
    # but for unit testing we can mock or just check retrieval
    retriever = rag_service.get_retriever()
    results = retriever.invoke("What is the capital of France?")
    assert len(results) > 0
    assert "Paris" in results[0].page_content
