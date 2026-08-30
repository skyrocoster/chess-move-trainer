from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.features.openings.api_schemas import (
    FilterDeclaration,
    GroupNode,
    LineLibraryResponse,
    LineNode,
    ReferenceNode,
    SortDeclaration,
)
from backend.app.features.openings.contract import (
    APPEARS_IN_MY_GAMES_FILTER_KEY,
    FIXED_CORPUS_SUBJECT_PLAYER_UUID,
    CatalogIdentity,
    PositionIdentity,
    TranspositionAppearance,
    TranspositionLink,
    canonical_transposition_presentation,
    decode_catalog_node_id,
    encode_catalog_node_id,
)
from backend.app.features.positions.repository import SUBJECT_PLAYER_UUID

MANIFEST = "manifest-accepted"
POSITION = PositionIdentity("8/8/8/8/8/8/8/8", "w", "-", "-")


def identity(source_file: str, row: int) -> CatalogIdentity:
    return CatalogIdentity(MANIFEST, source_file, row)


def appearance(
    source_file: str,
    row: int,
    ply: int,
    uci_prefix: str,
) -> TranspositionAppearance:
    return TranspositionAppearance(identity(source_file, row), POSITION, ply, uci_prefix)


def valid_response() -> LineLibraryResponse:
    group_id = "fixture-group"
    line_id = "fixture-line"
    reference_id = "fixture-reference"
    return LineLibraryResponse(
        roots=[group_id],
        nodes={
            group_id: GroupNode(
                id=group_id,
                kind="group",
                selectable=True,
                child_ids=[line_id, reference_id],
                metadata={"label": "Fixture family"},
            ),
            line_id: LineNode(
                id=line_id,
                kind="line",
                metadata={"label": "Fixture line", "eco": "A00"},
            ),
            reference_id: ReferenceNode(
                id=reference_id,
                kind="reference",
                target_id=line_id,
                metadata={"label": "Transposition reference"},
            ),
        },
        filters=[
            FilterDeclaration(key="search", label="Search", type="search"),
            FilterDeclaration(
                key="eco",
                label="ECO",
                type="range",
                range_start="A00",
                range_end="E99",
            ),
            FilterDeclaration(
                key="appears_in_my_games",
                label="Appears in my games",
                type="toggle",
            ),
        ],
        sorts=[SortDeclaration(key="default", label="Default", default=True)],
        selection_limit=25,
    )


def test_normalized_response_uses_strict_authoritative_node_shape() -> None:
    response = valid_response()

    assert response.model_dump() == {
        "roots": ["fixture-group"],
        "nodes": {
            "fixture-group": {
                "id": "fixture-group",
                "kind": "group",
                "child_ids": ["fixture-line", "fixture-reference"],
                "disabled": False,
                "disabled_reason": None,
                "metadata": {"label": "Fixture family"},
                "selectable": True,
            },
            "fixture-line": {
                "id": "fixture-line",
                "kind": "line",
                "child_ids": [],
                "disabled": False,
                "disabled_reason": None,
                "metadata": {"label": "Fixture line", "eco": "A00"},
                "selectable": True,
            },
            "fixture-reference": {
                "id": "fixture-reference",
                "kind": "reference",
                "child_ids": [],
                "disabled": False,
                "disabled_reason": None,
                "metadata": {"label": "Transposition reference"},
                "selectable": False,
                "target_id": "fixture-line",
            },
        },
        "filters": [
            {
                "key": "search",
                "label": "Search",
                "type": "search",
                "options": [],
                "range_start": None,
                "range_end": None,
                "metadata": {},
            },
            {
                "key": "eco",
                "label": "ECO",
                "type": "range",
                "options": [],
                "range_start": "A00",
                "range_end": "E99",
                "metadata": {},
            },
            {
                "key": "appears_in_my_games",
                "label": "Appears in my games",
                "type": "toggle",
                "options": [],
                "range_start": None,
                "range_end": None,
                "metadata": {},
            },
        ],
        "filter_apply_mode": "immediate",
        "sorts": [{"key": "default", "label": "Default", "default": True, "direction": "asc"}],
        "selection_limit": 25,
    }


def test_appears_in_my_games_is_the_fixed_corpus_filter_without_authentication() -> None:
    declaration = next(
        declaration
        for declaration in valid_response().filters
        if declaration.key == APPEARS_IN_MY_GAMES_FILTER_KEY
    )

    assert declaration.type == "toggle"
    assert FIXED_CORPUS_SUBJECT_PLAYER_UUID == SUBJECT_PLAYER_UUID
    assert APPEARS_IN_MY_GAMES_FILTER_KEY == "appears_in_my_games"


def test_normalized_response_rejects_extra_fields_and_invalid_graph_links() -> None:
    with pytest.raises(ValidationError):
        GroupNode(id="group", kind="group", unexpected="not allowed")

    with pytest.raises(ValidationError, match="reference target_id"):
        LineLibraryResponse(
            roots=["reference"],
            nodes={
                "reference": ReferenceNode(id="reference", kind="reference", target_id="missing")
            },
        )

    with pytest.raises(ValidationError, match="acyclic"):
        LineLibraryResponse(
            roots=["group"],
            nodes={
                "group": GroupNode(id="group", kind="group", child_ids=["child"]),
                "child": GroupNode(id="child", kind="group", child_ids=["group"]),
            },
        )


def test_node_kinds_encode_disabled_reasons_and_reference_non_selectability() -> None:
    disabled = LineNode(
        id="disabled-line",
        kind="line",
        disabled=True,
        disabled_reason="Not eligible in this result",
    )
    reference = ReferenceNode(id="reference", kind="reference", target_id="line")

    assert disabled.disabled is True
    assert disabled.disabled_reason == "Not eligible in this result"
    assert reference.selectable is False

    with pytest.raises(ValidationError, match="disabled_reason"):
        LineNode(id="bad-disabled", kind="line", disabled=True)
    with pytest.raises(ValidationError, match="cannot be disabled"):
        ReferenceNode(
            id="bad-reference",
            kind="reference",
            target_id="line",
            disabled=True,
            disabled_reason="References are not selectable",
        )


def test_opaque_catalog_id_round_trips_the_full_authoritative_composite_identity() -> None:
    selected = identity("b.tsv", 17)
    node_id = encode_catalog_node_id(selected)

    assert node_id.startswith("ol1_")
    assert decode_catalog_node_id(node_id) == selected
    assert encode_catalog_node_id(selected) == node_id
    assert encode_catalog_node_id(identity("b.tsv", 18)) != node_id
    assert encode_catalog_node_id(CatalogIdentity("other-manifest", "b.tsv", 17)) != node_id


def test_transposition_presentation_assigns_one_canonical_location_per_identity() -> None:
    first = appearance("a.tsv", 1, 8, "e4 e5")
    later = appearance("a.tsv", 1, 12, "e4 e5 Nf3 Nc6")
    other = appearance("b.tsv", 2, 10, "d4 d5")
    links = [
        TranspositionLink(first=first, second=other),
        TranspositionLink(first=later, second=other),
    ]

    presentation = canonical_transposition_presentation(links)
    canonical = dict(presentation.canonical_by_identity)

    assert canonical[identity("a.tsv", 1)] == first
    assert canonical[identity("b.tsv", 2)] == other
    assert len(presentation.references) == 1
    reference = presentation.references[0]
    assert reference.appearance == later
    assert reference.target_id == encode_catalog_node_id(identity("a.tsv", 1))
    assert reference.node_id != reference.target_id


def test_transposition_presentation_is_order_independent_and_does_not_invent_links() -> None:
    first = appearance("a.tsv", 1, 8, "e4 e5")
    later = appearance("a.tsv", 1, 12, "e4 e5 Nf3 Nc6")
    other = appearance("b.tsv", 2, 10, "d4 d5")
    forward = [
        TranspositionLink(first=first, second=other),
        TranspositionLink(first=later, second=other),
    ]
    reversed_links = list(reversed(forward))

    assert canonical_transposition_presentation(forward) == canonical_transposition_presentation(
        reversed_links
    )
    assert all(
        reference.appearance in {first, later, other}
        for reference in canonical_transposition_presentation(forward).references
    )
