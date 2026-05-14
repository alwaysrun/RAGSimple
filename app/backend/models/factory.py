from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from app.backend.core.config import settings
import os

class ModelFactory:
    @staticmethod
    def get_llm():
        """
        Returns a LangChain-compatible LLM instance.
        Currently supports Ali-Bailian (DashScope) via OpenAI-compatible API.
        """
        if settings.models.llm_type == "openai":
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("DASHSCOPE_API_KEY not found in environment")
                
            return ChatOpenAI(
                model=settings.models.llm_model,
                openai_api_key=api_key,
                openai_api_base=settings.models.llm_base_url
            )
        raise ValueError(f"Unsupported LLM type: {settings.models.llm_type}")

    @staticmethod
    def get_embeddings():
        """
        Returns a LangChain-compatible Embeddings instance.
        Currently supports local models via HuggingFaceEmbeddings.
        """
        if settings.models.embedding_type == "huggingface":
            return HuggingFaceEmbeddings(
                model_name=settings.models.embedding_model,
                # Ensure it runs on CPU if no GPU is available, or can be configured via toml
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        raise ValueError(f"Unsupported embedding type: {settings.models.embedding_type}")
