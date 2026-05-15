from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.backend.models.factory import ModelFactory
from app.backend.core.config import settings

def process_documents(docs):
    """
    Processes documents using Semantic Chunking.
    """
    from langchain_experimental.text_splitter import SemanticChunker
    embeddings = ModelFactory.get_embeddings()
    # Semantic chunking for better context
    semantic_splitter = SemanticChunker(
        embeddings, 
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=settings.rag.semantic_threshold
    )
    chunks = semantic_splitter.split_documents(docs)
    return chunks

def get_parent_child_chunks():
    """
    Returns the splitters for Parent-Child indexing.
    """
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=200
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, 
        chunk_overlap=50
    )
    
    return parent_splitter, child_splitter
