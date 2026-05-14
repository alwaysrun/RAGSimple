import requests
import io
from typing import List, Dict, Any

class RAGClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def query(self, text: str) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/query", json={"query": text})
        response.raise_for_status()
        return response.json()

    def ingest(self, files: List[tuple]) -> Dict[str, Any]:
        """
        files: List of (filename, bytes)
        """
        multipart_files = [
            ("files", (name, content)) for name, content in files
        ]
        response = requests.post(f"{self.base_url}/ingest", files=multipart_files)
        response.raise_for_status()
        return response.json()

    def get_config(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/config")
        response.raise_for_status()
        return response.json()

    def reset(self) -> Dict[str, Any]:
        response = requests.delete(f"{self.base_url}/reset")
        response.raise_for_status()
        return response.json()
