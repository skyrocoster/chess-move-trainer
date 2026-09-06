"""Serial direct Tool analysis over the live on-demand target selection."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..analysis import AnalysisRepository, AnalysisResultInput, PublicationOutcome
from .configuration import TOOL_PROFILE
from .engine import StockfishAnalysis, StockfishEngine
from .mutex import DatabaseMutex
from .targets import (
    INITIAL_TECHNICAL_CATEGORIES,
    InitialAnalysisTargetSelector,
    BulkTarget,
    BulkTargetSelector,
    _validate_limit,
)


class BulkError(RuntimeError):
    """Base class for direct bulk-analysis failures."""


class BulkInputError(BulkError, ValueError):
    """Raised when bulk runner input is invalid."""


@dataclass(frozen=True, slots=True)
class BulkFailure:
    """One isolated target failure retained only in the in-memory outcome."""

    position_id: int
    message: str


@dataclass(frozen=True, slots=True)
class BulkOutcome:
    """Observable result of one serial bulk launch."""

    selected_count: int
    published_count: int
    not_saved_count: int
    failures: tuple[BulkFailure, ...] = ()
    interrupted: bool = False
    preset: str | None = None
    technical_categories: tuple[str, ...] = ()

    @property
    def exit_code(self) -> int:
        """Return the later CLI-compatible status for this service outcome."""

        if self.interrupted:
            return 130
        return 1 if self.failures else 0

    @property
    def succeeded(self) -> bool:
        """Whether the launch completed without isolated failures or interruption."""

        return not self.failures and not self.interrupted


class BulkRunner:
    """Analyze eligible targets one at a time and publish each result immediately."""

    def __init__(
        self,
        database_path: str | Path,
        executable: str | Path,
        *,
        page_size: int = 100,
        lock_timeout: float = 5.0,
        _selector_factory: Callable[[str | Path, int, float], BulkTargetSelector]
        | None = None,
        _engine_factory: Callable[[], Any] | None = None,
        _publisher_factory: Callable[[], Any] | None = None,
        _mutex_factory: Callable[[str | Path], Any] | None = None,
        _initial_selector_factory: Callable[[str | Path, int, float], Any] | None = None,
    ) -> None:
        if not isinstance(executable, (str, Path)) or not str(executable):
            raise BulkInputError("executable must be an explicit path")
        self._database_path = database_path
        self._executable = executable
        self._page_size = page_size
        self._lock_timeout = lock_timeout
        self._selector_factory = _selector_factory or (
            lambda path, size, timeout: BulkTargetSelector(
                path,
                page_size=size,
                lock_timeout=timeout,
            )
        )
        self._engine_factory = _engine_factory or (
            lambda: StockfishEngine(self._executable)
        )
        self._publisher_factory = _publisher_factory or (
            lambda: AnalysisRepository(
                self._database_path,
                lock_timeout=self._lock_timeout,
            )
        )
        self._mutex_factory = _mutex_factory or (lambda path: DatabaseMutex(path))
        self._initial_selector_factory = _initial_selector_factory or (
            lambda path, size, timeout: InitialAnalysisTargetSelector(
                path,
                page_size=size,
                lock_timeout=timeout,
            )
        )

    def run(
        self,
        *,
        limit: int | None = None,
        preset: str | None = None,
    ) -> BulkOutcome:
        """Run the next eligible targets, or all eligible targets when unlimited."""

        _validate_limit(limit)
        if preset not in (None, "initial"):
            raise BulkInputError("preset must be 'initial' when supplied")
        if preset == "initial" and limit is not None:
            raise BulkInputError("--limit cannot be combined with the initial preset")

        selector_factory = (
            self._selector_factory
            if preset is None
            else self._initial_selector_factory
        )
        selector = selector_factory(
            self._database_path,
            self._page_size,
            self._lock_timeout,
        )
        targets = iter(selector.iter_targets(limit=limit))
        try:
            first_target = next(targets)
        except StopIteration:
            return BulkOutcome(
                0,
                0,
                0,
                preset=preset,
                technical_categories=(
                    INITIAL_TECHNICAL_CATEGORIES if preset == "initial" else ()
                ),
            )
        except KeyboardInterrupt:
            return BulkOutcome(
                0,
                0,
                0,
                interrupted=True,
                preset=preset,
                technical_categories=(
                    INITIAL_TECHNICAL_CATEGORIES if preset == "initial" else ()
                ),
            )

        selected_count = 0
        published_count = 0
        not_saved_count = 0
        failures: list[BulkFailure] = []
        interrupted = False

        with self._mutex_factory(self._database_path):
            engine = self._engine_factory()
            publisher = self._publisher_factory()
            try:
                for target in _prepend(first_target, targets):
                    selected_count += 1
                    try:
                        analysis = engine.analyze(target.position, TOOL_PROFILE)
                        result = _analysis_result(analysis)
                        outcome = publisher.publish(target.position_id, result)
                        if outcome.saved:
                            published_count += 1
                        else:
                            not_saved_count += 1
                    except KeyboardInterrupt:
                        interrupted = True
                        break
                    except Exception as error:
                        failures.append(
                            BulkFailure(position_id=target.position_id, message=str(error))
                        )
            finally:
                engine.close()

        return BulkOutcome(
            selected_count=selected_count,
            published_count=published_count,
            not_saved_count=not_saved_count,
            failures=tuple(failures),
            interrupted=interrupted,
            preset=preset,
            technical_categories=(
                INITIAL_TECHNICAL_CATEGORIES if preset == "initial" else ()
            ),
        )


SerialBulkRunner = BulkRunner


def _prepend(first: BulkTarget, rest: Iterator[BulkTarget]) -> Iterator[BulkTarget]:
    yield first
    yield from rest


def _analysis_result(analysis: StockfishAnalysis | AnalysisResultInput) -> AnalysisResultInput:
    if isinstance(analysis, StockfishAnalysis):
        return analysis.result
    if isinstance(analysis, AnalysisResultInput):
        return analysis
    candidate = getattr(analysis, "result", None)
    if isinstance(candidate, AnalysisResultInput):
        return candidate
    raise BulkError("engine did not return a normalized analysis result")


__all__ = [
    "BulkError",
    "BulkFailure",
    "BulkInputError",
    "BulkOutcome",
    "BulkRunner",
    "SerialBulkRunner",
]
