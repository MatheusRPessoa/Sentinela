from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.trends import router as trends_router
from backend.app.api.routes.signals import router as signals_router
from backend.app.api.routes.metadata import router as metadata_router
from backend.app.api.routes.options import router as options_router
from backend.app.api.routes.coverage import router as coverage_router
from backend.app.api.routes.operational_status import router as operational_status_router
from backend.app.api.routes.nowcast import router as nowcast_router




app = FastAPI(
    title="Sentinela API",
    description="API para monitoramento de tendências de SRAG",
    version="0.1.0"
)

app.include_router(trends_router)
app.include_router(signals_router)
app.include_router(metadata_router)
app.include_router(options_router)
app.include_router(coverage_router)
app.include_router(operational_status_router)
app.include_router(nowcast_router)


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
