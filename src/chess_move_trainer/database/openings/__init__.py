"""Public opening catalogue services."""

from .acquisition import (
    DEFAULT_REQUEST_DELAY,
    DEFAULT_REQUEST_TIMEOUT,
    HttpxOpeningAcquisitionTransport,
    OpeningAcquisitionError,
    OpeningAcquisitionFailure,
    OpeningAcquisitionResult,
    OpeningAcquisitionTransport,
    acquire_openings,
    validate_request_timing,
)
from .persistence import (
    CataloguePublication,
    OpeningCatalogueRepository,
    OpeningPersistenceError,
    import_opening_catalogue,
)
from .recognition import (
    MatchKind,
    OpeningInputError,
    OpeningRecognition,
    OpeningRecognitionError,
    RecognizedOpening,
    lookup_fen,
    replay_pgn,
)
from .source import OpeningRouteSource, OpeningSourceError, load_opening_sources

__all__ = [
    "CataloguePublication",
    "DEFAULT_REQUEST_DELAY",
    "DEFAULT_REQUEST_TIMEOUT",
    "HttpxOpeningAcquisitionTransport",
    "MatchKind",
    "OpeningCatalogueRepository",
    "OpeningAcquisitionError",
    "OpeningAcquisitionFailure",
    "OpeningAcquisitionResult",
    "OpeningAcquisitionTransport",
    "OpeningInputError",
    "OpeningPersistenceError",
    "OpeningRecognition",
    "OpeningRecognitionError",
    "OpeningRouteSource",
    "OpeningSourceError",
    "RecognizedOpening",
    "import_opening_catalogue",
    "acquire_openings",
    "load_opening_sources",
    "lookup_fen",
    "replay_pgn",
    "validate_request_timing",
]
