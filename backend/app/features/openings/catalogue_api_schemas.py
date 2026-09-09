"""Strict HTTP models for the clean opening catalogue collection."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class OpeningsModel(BaseModel):
    """Base model that rejects fields outside the clean catalogue contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


OpeningCatalogueErrorCode = Literal[
    "invalid_filter",
    "openings_unavailable",
    "unexpected_failure",
]

OpeningDetailErrorCode = Literal[
    "invalid_opening_key",
    "opening_not_found",
    "openings_unavailable",
    "unexpected_failure",
]


class OpeningCatalogueItemResponse(OpeningsModel):
    key: str
    eco: str
    name: str
    route_count: int
    games_reached: int
    games_deepest: int


class OpeningCatalogueResponse(OpeningsModel):
    items: list[OpeningCatalogueItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool


class OpeningCatalogueErrorResponse(OpeningsModel):
    code: OpeningCatalogueErrorCode
    message: str


class OpeningDetailErrorResponse(OpeningsModel):
    code: OpeningDetailErrorCode
    message: str


__all__ = [
    "OpeningCatalogueErrorCode",
    "OpeningCatalogueErrorResponse",
    "OpeningCatalogueItemResponse",
    "OpeningCatalogueResponse",
    "OpeningDetailErrorCode",
    "OpeningDetailErrorResponse",
]
