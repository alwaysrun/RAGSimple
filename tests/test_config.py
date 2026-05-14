import os
from app.backend.core.config import settings

def test_settings_load():
    # Verify that settings are loaded correctly from config.toml
    assert settings.backend.port == 8000
    assert settings.backend.host == "0.0.0.0"
    
    # Verify that .env is loaded (at least the key exists and has a value)
    assert "DASHSCOPE_API_KEY" in os.environ
    assert len(os.getenv("DASHSCOPE_API_KEY")) > 0
