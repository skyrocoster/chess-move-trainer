"""Opening recognition services and internal source/persistence modules."""

from .recognition import (
    MatchKind,
    OpeningInputError,
    OpeningRecognition,
    OpeningRecognitionError,
    RecognizedOpening,
    lookup_fen,
    replay_pgn,
)
from .keys import OpeningKeyError, opening_api_key, parse_opening_api_key
from .catalogue import (
    OpeningCatalogueEntry,
    OpeningCatalogueError,
    OpeningCataloguePage,
    OpeningCatalogueQuery,
    OpeningCatalogueReader,
    OpeningCatalogueSchemaError,
    OpeningCatalogueSort,
    OpeningCatalogueStorageError,
    OpeningCatalogueValidationError,
    read_opening,
    read_openings,
)
from .persistence import OpeningCatalogueRepository
from .source import OpeningRouteSource, OpeningSourceError, load_opening_sources

__all__ = [
    "MatchKind",
    "OpeningKeyError",
    "OpeningCatalogueEntry",
    "OpeningCatalogueError",
    "OpeningCataloguePage",
    "OpeningCatalogueQuery",
    "OpeningCatalogueReader",
    "OpeningCatalogueRepository",
    "OpeningCatalogueSchemaError",
    "OpeningCatalogueSort",
    "OpeningCatalogueStorageError",
    "OpeningCatalogueValidationError",
    "OpeningInputError",
    "OpeningRecognition",
    "OpeningRecognitionError",
    "OpeningRouteSource",
    "OpeningSourceError",
    "RecognizedOpening",
    "load_opening_sources",
    "opening_api_key",
    "parse_opening_api_key",
    "lookup_fen",
    "replay_pgn",
    "read_opening",
    "read_openings",
]
