from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from backend.app.features.positions.repository import (
    CorpusUnavailableError,
    PositionNotFoundError,
    StoredPositionInvalidError,
    fetch_position,
)
from backend.app.features.positions.schemas import (
    PositionErrorResponse,
    PositionResponse,
)

router = APIRouter(prefix="/api", tags=["positions"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = PositionErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


@router.get(
    "/games/{game_uuid}/positions/{ply}",
    response_model=PositionResponse,
    responses={
        404: {"model": PositionErrorResponse},
        500: {"model": PositionErrorResponse},
        503: {"model": PositionErrorResponse},
    },
)
def position(game_uuid: UUID, ply: Annotated[int, Path(ge=0)]) -> PositionResponse | JSONResponse:
    try:
        stored_position = fetch_position(game_uuid, ply)
    except PositionNotFoundError:
        return _error(404, "position_not_found", "Position not found")
    except CorpusUnavailableError:
        return _error(503, "corpus_unavailable", "Corpus unavailable")
    except StoredPositionInvalidError:
        return _error(500, "stored_position_invalid", "Stored position unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to load position")

    return PositionResponse(
        game_uuid=stored_position.game_uuid,
        ply=stored_position.ply,
        fen=stored_position.fen,
        subject_color=stored_position.subject_color,
    )
