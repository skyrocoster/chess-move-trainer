from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.features.evaluation.router import router as evaluation_router
from backend.app.features.health.router import router as health_router
from backend.app.features.positions.router import router as positions_router


def create_app() -> FastAPI:
    app = FastAPI(title="Chess Move Trainer")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8444"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(health_router)
    app.include_router(positions_router)
    app.include_router(evaluation_router)
    return app


app = create_app()
