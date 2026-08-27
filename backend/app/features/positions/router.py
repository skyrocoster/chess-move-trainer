from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.app.features.positions.repository import (
    CorpusUnavailableError,
    GameNotFoundError,
    GameUnavailableError,
    PositionNotFoundError,
    fetch_game,
)
from backend.app.features.positions.schemas import (
    GameErrorResponse,
    GameResponse,
)

router = APIRouter(prefix="/api", tags=["positions"])


def _game_error(status_code: int, code: str, message: str) -> JSONResponse:
    body = GameErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


@router.get(
    "/games/{game_uuid}/positions",
    response_model=GameResponse,
    responses={
        404: {"model": GameErrorResponse},
        500: {"model": GameErrorResponse},
        503: {"model": GameErrorResponse},
    },
)
def game_positions(
    game_uuid: UUID,
    ply: Annotated[int | None, Query(ge=0)] = None,
) -> GameResponse | JSONResponse:
    initial_ply = 0 if ply is None else ply
    try:
        stored_game = fetch_game(game_uuid, initial_ply)
    except GameNotFoundError:
        return _game_error(404, "game_not_found", "Game not found")
    except PositionNotFoundError:
        return _game_error(404, "position_not_found", "Position not found")
    except CorpusUnavailableError:
        return _game_error(503, "corpus_unavailable", "Corpus unavailable")
    except GameUnavailableError:
        return _game_error(500, "game_unavailable", "Game unavailable")
    except Exception:
        return _game_error(500, "unexpected_failure", "Unable to load game")

    return GameResponse(
        game_uuid=stored_game.game_uuid,
        initial_ply=stored_game.initial_ply,
        subject_color=stored_game.subject_color,
        source_url=stored_game.source_url,
        positions=[
            {"ply": position.ply, "fen": position.fen, "san": position.san}
            for position in stored_game.positions
        ],
    )
