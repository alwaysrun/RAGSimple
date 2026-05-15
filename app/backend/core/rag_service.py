print("📚 Loading heavy RAG dependencies...")
import os

print("  ├─ Loading LangChain retrievers & storage...")
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

print("  ├─ Loading Vector Store (ChromaDB)...")
from langchain_chroma import Chroma

print("  └─ Loading Internal Modules...")
from app.backend.models.factory import ModelFactory
from app.backend.core.config import settings
from app.backend.core.ingestion import get_parent_child_chunks

class RAGService:
    def __init__(self):
        print("🛠️  Initializing RAG Service...")
        self.embeddings = ModelFactory.get_embeddings()
        
        # Setup paths
        db_path = settings.backend.db_path
        store_path = os.path.join(os.path.dirname(db_path), "docstore")
        os.makedirs(db_path, exist_ok=True)
        os.makedirs(store_path, exist_ok=True)
        
        # Initialize VectorStore
        self.vectorstore = Chroma(
            collection_name="rag_simple",
            persist_directory=db_path, 
            embedding_function=self.embeddings
        )
        
        # Initialize DocStore (Local File System)
        fs = LocalFileStore(store_path)
        self.docstore = create_kv_docstore(fs)
        
        # Initialize ParentDocumentRetriever
        parent_splitter, child_splitter = get_parent_child_chunks()
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )

    def ingest(self, docs):
        """
        Ingests documents into the Parent-Child system.
        """
        self.retriever.add_documents(docs, ids=None)

    def get_retriever(self):
        return self.retriever

    def query(self, query_text):
        """
        Executes a RAG query.
        """
        from langchain.chains import RetrievalQA
        llm = ModelFactory.get_llm()
        qa = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type="stuff", 
            retriever=self.retriever,
            return_source_documents=True
        )
        return qa.invoke({"query": query_text})

    def reset(self):
        """
        Resets the vector store and docstore.
        """
        # Note: In a real app, you might want a more thorough cleanup
        self.vectorstore.delete_collection()
        # Re-initialize collection
        self.vectorstore = Chroma(
            collection_name="rag_simple",
            persist_directory=settings.backend.db_path, 
            embedding_function=self.embeddings
        )
