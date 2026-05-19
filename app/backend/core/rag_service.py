import logging
import os
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading heavy RAG dependencies...")

logger.info("  Loading LangChain retrievers & storage...")
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore

logger.info("  Loading Vector Store (ChromaDB)...")
from langchain_chroma import Chroma

logger.info("  Loading Conversation Memory...")
from langchain_community.chat_message_histories import ChatMessageHistory

logger.info("  Loading Internal Modules...")
from app.backend.models.factory import ModelFactory
from app.backend.core.config import settings
from app.backend.core.ingestion import get_parent_child_chunks, process_documents

def _generate_doc_id(doc, index: int) -> str:
    """
    Generate a deterministic ID for a document based on its content and metadata.
    This prevents duplicate ingestion of the same document.
    """
    content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
    source = doc.metadata.get('source', 'unknown')
    page = doc.metadata.get('page', 0)
    return f"{source}_{page}_{content_hash}_{index}"

class RAGService:
    def __init__(self):
        logger.info("Initializing RAG Service...")
        self.embeddings = ModelFactory.get_embeddings()
        
        self.db_path = settings.backend.db_path
        self.store_path = os.path.join(os.path.dirname(self.db_path), "docstore")
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.store_path, exist_ok=True)
        
        self.vectorstore = Chroma(
            collection_name="rag_simple",
            persist_directory=self.db_path, 
            embedding_function=self.embeddings
        )
        
        fs = LocalFileStore(self.store_path)
        self.docstore = create_kv_docstore(fs)
        
        parent_splitter, child_splitter = get_parent_child_chunks()
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
        
        self.chat_history = ChatMessageHistory()
        self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt from configuration.
        Uses custom prompt template if available, otherwise builds from components.
        """
        if settings.prompt.full_system_prompt:
            self.system_prompt_template = settings.prompt.full_system_prompt
        else:
            self.system_prompt_template = f"""{settings.prompt.system_role}

{settings.prompt.answer_constraints}

{settings.prompt.language_optimization}

以下是检索到的相关文档内容：
{{context}}"""
        return self.system_prompt_template

    def ingest(self, docs):
        """
        Ingests documents into the Parent-Child system.
        First applies semantic chunking, then adds to the retriever.
        Generates deterministic IDs to prevent duplicate ingestion.
        """
        chunks = process_documents(docs)
        doc_ids = [_generate_doc_id(doc, idx) for idx, doc in enumerate(chunks)]
        self.retriever.add_documents(chunks, ids=doc_ids)

    def get_retriever(self):
        return self.retriever
    
    def _retrieve_with_relevance_filter(self, query_text: str) -> list:
        """
        Retrieve documents with relevance score filtering.
        Returns only documents above the relevance threshold.
        """
        docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(
            query_text,
            k=settings.prompt.top_k,
            score_threshold=settings.prompt.relevance_threshold
        )
        return docs_with_scores

    def query(self, query_text: str, use_history: bool = True) -> dict:
        """
        Executes a RAG query using modern LCEL with custom prompt and conversation memory.
        
        Args:
            query_text: The user query
            use_history: Whether to include conversation history (default: True)
        
        Returns:
            dict with 'answer', 'source_documents', and 'context_used' keys
        """
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.documents import Document
        
        llm = ModelFactory.get_llm()
        
        docs_with_scores = self._retrieve_with_relevance_filter(query_text)
        if not docs_with_scores:
            return {
                "answer": "抱歉，我没有找到与您问题相关的内容。请尝试用不同的方式提问，或者上传相关文档。",
                "source_documents": [],
                "context_used": False
            }
        
        filtered_docs = [doc for doc, score in docs_with_scores]
        
        messages = [("system", self.system_prompt_template)]
        
        if use_history:
            for msg in self.chat_history.messages:
                messages.append((msg.type, msg.content))
        
        messages.append(("human", "{input}"))
        
        prompt = ChatPromptTemplate.from_messages(messages)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        
        context = "\n\n".join([doc.page_content for doc in filtered_docs])
        
        result = document_chain.invoke({
            "input": query_text,
            "context": context
        })
        
        if use_history:
            from langchain_core.messages import HumanMessage, AIMessage
            self.chat_history.add_message(HumanMessage(content=query_text))
            self.chat_history.add_message(AIMessage(content=result))
        
        return {
            "answer": result,
            "source_documents": filtered_docs,
            "context_used": True
        }
    
    def clear_history(self):
        """
        Clear conversation history for a new session.
        """
        self.chat_history.clear()

    def reset(self):
        """
        Resets the vector store and docstore.
        """
        # Delete ChromaDB collection
        self.vectorstore.delete_collection()
        
        # Clear docstore files
        if os.path.exists(self.store_path):
            for filename in os.listdir(self.store_path):
                filepath = os.path.join(self.store_path, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        
        # Re-initialize VectorStore
        self.vectorstore = Chroma(
            collection_name="rag_simple",
            persist_directory=self.db_path, 
            embedding_function=self.embeddings
        )
        
        # Re-initialize DocStore
        fs = LocalFileStore(self.store_path)
        self.docstore = create_kv_docstore(fs)
        
        # Re-initialize ParentDocumentRetriever
        parent_splitter, child_splitter = get_parent_child_chunks()
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
