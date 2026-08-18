"""Exception types for the Chess.com position-corpus extractor."""

from __future__ import annotations


class CorpusSchemaError(RuntimeError):
    """The existing corpus schema cannot be used by this extractor version."""


class CorpusReplayError(ValueError):
    """A source game cannot produce a valid ordered corpus build."""


class CorpusBusyError(RuntimeError):
    """The database is locked by another fetch or extraction writer."""

    MESSAGE = "database is busy (concurrent fetch or extraction); retry later"


ReplayError = CorpusReplayError
