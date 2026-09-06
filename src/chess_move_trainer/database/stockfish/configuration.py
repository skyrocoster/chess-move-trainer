"""The fixed Stockfish profiles supported by the first database worker."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ..analysis import AnalysisQuality


STOCKFISH_NAME = "Stockfish"
STOCKFISH_VERSION = "18"
CONFIGURATION_VERSION = 1
MULTI_PV = 5
THREADS = 6
HASH_MB = 1024
BROWSER_NODES = 200_000
TOOL_NODES = 6_400_000


@dataclass(frozen=True, slots=True)
class StockfishProfile:
    """One immutable, result-affecting Stockfish search profile."""

    quality: AnalysisQuality
    nodes: int
    threads: int = THREADS
    hash_mb: int = HASH_MB
    multipv: int = MULTI_PV
    configuration_version: int = CONFIGURATION_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "quality", AnalysisQuality(self.quality))
        for name, value in (
            ("nodes", self.nodes),
            ("threads", self.threads),
            ("hash_mb", self.hash_mb),
            ("multipv", self.multipv),
            ("configuration_version", self.configuration_version),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @property
    def uci_options(self) -> Mapping[str, int | bool]:
        """Return the UCI options applied before a search."""

        return MappingProxyType(
            {
                "Threads": self.threads,
                "Hash": self.hash_mb,
                "MultiPV": self.multipv,
                "UCI_ShowWDL": True,
            }
        )

    @property
    def settings(self) -> Mapping[str, int | bool]:
        """Return the complete normalized settings stored with an analysis."""

        return MappingProxyType(
            {
                "Hash": self.hash_mb,
                "MultiPV": self.multipv,
                "Nodes": self.nodes,
                "Threads": self.threads,
                "UCI_ShowWDL": True,
            }
        )


BROWSER_PROFILE = StockfishProfile(AnalysisQuality.BROWSER, BROWSER_NODES)
TOOL_PROFILE = StockfishProfile(AnalysisQuality.TOOL, TOOL_NODES)
PROFILES: Mapping[AnalysisQuality, StockfishProfile] = MappingProxyType(
    {
        AnalysisQuality.BROWSER: BROWSER_PROFILE,
        AnalysisQuality.TOOL: TOOL_PROFILE,
    }
)


def profile_for(value: StockfishProfile | AnalysisQuality | str) -> StockfishProfile:
    """Resolve one of the approved fixed profiles."""

    if isinstance(value, StockfishProfile):
        return value
    try:
        return PROFILES[AnalysisQuality(value)]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("profile must be the approved browser or tool profile") from error


__all__ = [
    "BROWSER_NODES",
    "BROWSER_PROFILE",
    "CONFIGURATION_VERSION",
    "HASH_MB",
    "MULTI_PV",
    "PROFILES",
    "STOCKFISH_NAME",
    "STOCKFISH_VERSION",
    "THREADS",
    "TOOL_NODES",
    "TOOL_PROFILE",
    "StockfishProfile",
    "profile_for",
]
