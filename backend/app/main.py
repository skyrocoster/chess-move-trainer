from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.features.analysis_observation.router import router as analysis_observation_router
from backend.app.features.analysis_requests.router import router as analysis_requests_router
from backend.app.features.evaluation.router import router as evaluation_router
from backend.app.features.games.router import router as games_router
from backend.app.features.health.router import router as health_router
from backend.app.features.move_response_distribution.router import (
    router as move_response_distribution_router,
)
from backend.app.features.openings.router import router as openings_router
from backend.app.features.position_context.router import router as position_context_router
from backend.app.features.position_insight.router import router as position_insight_router
from backend.app.features.positions.router import router as positions_router
from backend.app.features.preferred_move.router import router as preferred_move_router
from backend.app.features.preferred_moves.router import router as preferred_moves_router


def create_app() -> FastAPI:
    app = FastAPI(title="Chess Move Trainer")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8444"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
    )
    app.include_router(health_router)
    app.include_router(games_router)
    app.include_router(positions_router)
    app.include_router(analysis_observation_router)
    app.include_router(analysis_requests_router)
    app.include_router(evaluation_router)
    app.include_router(preferred_move_router)
    app.include_router(preferred_moves_router)
    app.include_router(position_context_router)
    app.include_router(position_insight_router)
    app.include_router(move_response_distribution_router)
    app.include_router(openings_router)
    return app


app = create_app()
