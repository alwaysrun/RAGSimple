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
    parent_chunk_size: int = 2000
    child_chunk_size: int = 400
    chunk_overlap_ratio: float = 0.1
    semantic_threshold: float = 0.5

class ModelSettings(BaseModel):
    llm_type: str = "openai"
    llm_model: str = "qwen-max"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_type: str = "huggingface"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_cache_dir: str = "data/models"

class PromptSettings(BaseModel):
    system_role: str = "你是一个专业的文档问答助手，专门帮助用户理解和查询文档内容。"
    answer_constraints: str = "请严格遵循以下规则：\n1. 仅基于检索到的文档内容回答问题，不要编造或添加文档中不存在的信息\n2. 如果检索到的内容不足以回答问题，请明确告知用户\n3. 回答要准确、简洁、有条理"
    language_optimization: str = "优化要求：\n- 使用清晰规范的中文表达\n- 避免口语化和非正式用语\n- 保持回答的结构化和逻辑性"
    full_system_prompt: str = ""
    relevance_threshold: float = 0.7
    top_k: int = 4

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
        
        prompt_config_path = os.path.join(CONFIG_DIR, "prompt.toml")
        if os.path.exists(prompt_config_path):
            with open(prompt_config_path, "r", encoding="utf-8") as f:
                prompt_config = toml.load(f)
            prompt_data = prompt_config.get("prompt", {})
            template_data = prompt_config.get("prompt", {}).get("template", {})
            retrieval_data = prompt_config.get("prompt", {}).get("retrieval", {})
            
            merged_prompt = {
                "system_role": prompt_data.get("system_role", ""),
                "answer_constraints": prompt_data.get("answer_constraints", ""),
                "language_optimization": prompt_data.get("language_optimization", ""),
                "full_system_prompt": template_data.get("full_system_prompt", ""),
                "relevance_threshold": retrieval_data.get("relevance_threshold", 0.7),
                "top_k": retrieval_data.get("top_k", 4)
            }
            self.prompt = PromptSettings(**merged_prompt)
        else:
            self.prompt = PromptSettings()

settings = Settings()
