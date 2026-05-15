import os
import toml
from pydantic import BaseModel
from dotenv import load_dotenv

# Path to the configures directory
CONFIG_DIR = os.path.join(os.getcwd(), "configures")
ENV_PATH = os.path.join(CONFIG_DIR, ".env")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.toml")

# Load environment variables from .env
load_dotenv(ENV_PATH)

class BackendSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    db_path: str = "data/DB"

class FrontendSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8501

class RAGSettings(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    semantic_threshold: float = 0.5

class ModelSettings(BaseModel):
    llm_type: str = "openai"
    llm_model: str = "qwen-max"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_type: str = "huggingface"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_cache_dir: str = "data/models"

class Settings:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")
            
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = toml.load(f)
            
        self.backend = BackendSettings(**config.get("backend", {}))
        self.frontend = FrontendSettings(**config.get("frontend", {}))
        self.rag = RAGSettings(**config.get("rag", {}))
        self.models = ModelSettings(**config.get("models", {}))

settings = Settings()
