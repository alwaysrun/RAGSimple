"""
RAGSimple Entry Point
This script serves as the main entry point for starting the RAGSimple application.
It can start either the Backend (FastAPI) or the Frontend (Streamlit).
"""
import os
import sys
import argparse
import subprocess
import uvicorn

# Ensure the root directory is in sys.path to allow absolute imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

def run_backend():
    """
    Starts the FastAPI backend server using uvicorn.
    """
    from app.backend.core.config import settings
    
    print(f"🚀 Starting RAGSimple Backend...")
    print(f"📍 Host: {settings.backend.host}")
    print(f"📍 Port: {settings.backend.port}")
    print(f"📍 LLM: {settings.models.llm_model}")
    
    # We use the string import format to enable uvicorn's reload feature
    uvicorn.run(
        "app.backend.api.main:app",
        host=settings.backend.host,
        port=settings.backend.port,
        reload=True
    )

def run_frontend():
    """
    Starts the Streamlit frontend.
    """
    from app.backend.core.config import settings
    
    print("🎨 Starting RAGSimple Frontend...")
    print(f"📍 Host: {settings.frontend.host}")
    print(f"📍 Port: {settings.frontend.port}")
    
    # Path to the frontend main file
    frontend_path = os.path.join(ROOT_DIR, "app", "frontend", "main.py")
    
    if not os.path.exists(frontend_path):
        print(f"❌ Error: Frontend entry point not found at {frontend_path}")
        sys.exit(1)
        
    # Command to run streamlit
    # Configuration is pulled from the TOML file via settings
    cmd = [
        sys.executable, "-m", "streamlit", "run", frontend_path,
        "--server.address", settings.frontend.host,
        "--server.port", str(settings.frontend.port),
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nFrontend stopped by user.")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="RAGSimple - A Simple RAG Application")
    parser.add_argument(
        "mode", 
        choices=["backend", "frontend"], 
        default="backend", 
        nargs="?",
        help="Mode to run: 'backend' (default) starts the API, 'frontend' starts the UI"
    )
    
    args = parser.parse_args()
    
    if args.mode == "backend":
        run_backend()
    elif args.mode == "frontend":
        run_frontend()

if __name__ == "__main__":
    main()
