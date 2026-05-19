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
                api_key=api_key,
                base_url=settings.models.llm_base_url
            )
        raise ValueError(f"Unsupported LLM type: {settings.models.llm_type}")

    @staticmethod
    def get_embeddings():
        """
        Returns a LangChain-compatible Embeddings instance.
        First tries to load from local cache to avoid network checks.
        Falls back to remote download if local files are missing.
        """
        if settings.models.embedding_type == "huggingface":
            cache_folder = os.path.abspath(settings.models.embedding_cache_dir)
            os.makedirs(cache_folder, exist_ok=True)
            model_name = settings.models.embedding_model
            common_kwargs = {
                "model_name": model_name,
                "cache_folder": cache_folder,
                "encode_kwargs": {'normalize_embeddings': True}
            }
            print(f"🧬 Loading Embedding Model: {model_name}...")
            
            try:
                # 1. Attempt to load strictly from local cache (no network checks)
                embeddings = HuggingFaceEmbeddings(
                    **common_kwargs,
                    model_kwargs={'device': 'cpu', 'local_files_only': True}
                )
                print(f"📂 Loaded Embedding Model from local cache: {cache_folder}")
                return embeddings
            except Exception:
                # 2. Fallback to remote load if local cache is missing or invalid
                print(f"🌐 Model '{model_name}' not found locally or cache invalid. Downloading...")
                return HuggingFaceEmbeddings(
                    **common_kwargs,
                    model_kwargs={'device': 'cpu', 'local_files_only': False}
                )
        
        raise ValueError(f"Unsupported embedding type: {settings.models.embedding_type}")
