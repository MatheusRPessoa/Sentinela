from fastapi import FastAPI

from backend.app.api.routes.trends import router as trends_router
from backend.app.api.routes.signals import router as signals_router
from backend.app.api.routes.metadata import router as metadata_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sentinela API",
    description="API para monitoramento de tendências de SRAG",
    version="0.1.0"
)

app.include_router(trends_router)
app.include_router(signals_router)
app.include_router(metadata_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sentinela-api"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
