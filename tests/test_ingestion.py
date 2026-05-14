from langchain_core.documents import Document
from app.backend.core.ingestion import process_documents, get_parent_child_chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

def test_process_documents_semantic():
    docs = [Document(page_content="This is a test document about artificial intelligence. AI is changing the world.")]
    chunks = process_documents(docs)
    assert len(chunks) > 0
    assert isinstance(chunks[0], Document)

def test_get_parent_child_chunks():
    docs = [Document(page_content="A very long document " * 100)]
    parent_splitter, child_splitter = get_parent_child_chunks()
    
    parents = parent_splitter.split_documents(docs)
    assert len(parents) > 0
    
    children = child_splitter.split_documents(parents)
    assert len(children) > len(parents)
    assert isinstance(child_splitter, RecursiveCharacterTextSplitter)
