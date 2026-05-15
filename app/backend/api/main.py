print("🔥 Backend process started, loading components...")
import uvicorn
from fastapi import FastAPI
from app.backend.api.routes import router
from app.backend.core.config import settings

app = FastAPI(title="RAGSimple API")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.backend.api.main:app", host=settings.backend.host, port=settings.backend.port, reload=False)
