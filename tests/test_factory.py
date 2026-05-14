from app.backend.models.factory import ModelFactory
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

def test_get_llm():
    llm = ModelFactory.get_llm()
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "glm-5"

def test_get_embeddings():
    embeddings = ModelFactory.get_embeddings()
    assert isinstance(embeddings, HuggingFaceEmbeddings)
    # Check if it has the required methods
    assert hasattr(embeddings, "embed_query")
    assert hasattr(embeddings, "embed_documents")
