from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.backend.models.factory import ModelFactory
from app.backend.core.config import settings

def process_documents(docs):
    """
    Processes documents using Semantic Chunking.
    Splits documents into semantic chunks for better context preservation.
    """
    from langchain_experimental.text_splitter import SemanticChunker
    embeddings = ModelFactory.get_embeddings()
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
    Uses config values from settings.rag for chunk parameters.
    Overlap is calculated as: chunk_size * chunk_overlap_ratio
    """
    ratio = settings.rag.chunk_overlap_ratio
    
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag.parent_chunk_size,
        chunk_overlap=int(settings.rag.parent_chunk_size * ratio)
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag.child_chunk_size,
        chunk_overlap=int(settings.rag.child_chunk_size * ratio)
    )
    
    return parent_splitter, child_splitter
