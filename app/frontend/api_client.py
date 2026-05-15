import requests
import io
from typing import List, Dict, Any

class RAGClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                detail = response.json().get("detail", str(e))
                raise Exception(detail)
            except Exception:
                raise Exception(f"{e.response.status_code} {e.response.reason}: {response.text}")

    def query(self, text: str) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/query", json={"query": text})
        return self._handle_response(response)

    def ingest(self, files: List[tuple]) -> Dict[str, Any]:
        """
        files: List of (filename, bytes)
        """
        multipart_files = [
            ("files", (name, content)) for name, content in files
        ]
        response = requests.post(f"{self.base_url}/ingest", files=multipart_files)
        return self._handle_response(response)

    def get_config(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/config")
        return self._handle_response(response)

    def reset(self) -> Dict[str, Any]:
        response = requests.delete(f"{self.base_url}/reset")
        return self._handle_response(response)
