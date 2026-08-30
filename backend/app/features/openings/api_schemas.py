"""Strict normalized transport schemas for the opening Line Library."""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

ScalarValue: TypeAlias = StrictStr | StrictInt | StrictFloat | StrictBool | None
FilterValue: TypeAlias = ScalarValue | list[StrictStr]
NodeKind: TypeAlias = Literal["group", "line", "reference"]
FilterType: TypeAlias = Literal["search", "select", "multiselect", "toggle", "range", "custom"]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class FilterOption(ContractModel):
    value: StrictStr
    label: StrictStr


class FilterDeclaration(ContractModel):
    key: StrictStr
    label: StrictStr
    type: FilterType
    options: list[FilterOption] = Field(default_factory=list)
    range_start: ScalarValue = None
    range_end: ScalarValue = None
    metadata: dict[StrictStr, ScalarValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_shape(self) -> "FilterDeclaration":
        if self.type in {"search", "toggle"} and (
            self.options or self.range_start is not None or self.range_end is not None
        ):
            raise ValueError(f"{self.type} filters cannot declare options or a range")
        if self.type in {"select", "multiselect"} and (
            not self.options or self.range_start is not None or self.range_end is not None
        ):
            raise ValueError(f"{self.type} filters require options and no range")
        if self.type == "range" and (
            self.options or self.range_start is None or self.range_end is None
        ):
            raise ValueError("range filters require bounds and no options")
        if self.type == "range" and self.range_start == self.range_end:
            raise ValueError("range bounds must differ")
        if (
            self.type == "custom"
            and self.options
            and (self.range_start is not None or self.range_end is not None)
        ):
            raise ValueError("custom filters cannot declare options and a range together")
        return self


class SortDeclaration(ContractModel):
    key: StrictStr
    label: StrictStr
    default: StrictBool = False
    direction: Literal["asc", "desc"] = "asc"


class NodeBase(ContractModel):
    id: StrictStr
    child_ids: list[StrictStr] = Field(default_factory=list)
    disabled: StrictBool = False
    disabled_reason: StrictStr | None = None
    metadata: dict[StrictStr, ScalarValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_disabled_reason(self) -> "NodeBase":
        if self.disabled and not self.disabled_reason:
            raise ValueError("disabled nodes require disabled_reason")
        if not self.disabled and self.disabled_reason is not None:
            raise ValueError("enabled nodes cannot declare disabled_reason")
        return self


class GroupNode(NodeBase):
    kind: Literal["group"]
    selectable: StrictBool = False


class LineNode(NodeBase):
    kind: Literal["line"]
    selectable: Literal[True] = True

    @model_validator(mode="after")
    def validate_leaf(self) -> "LineNode":
        if self.child_ids:
            raise ValueError("line nodes cannot have children")
        return self


class ReferenceNode(NodeBase):
    kind: Literal["reference"]
    target_id: StrictStr
    selectable: Literal[False] = False

    @model_validator(mode="after")
    def validate_pointer(self) -> "ReferenceNode":
        if self.child_ids:
            raise ValueError("reference nodes cannot have children")
        if self.disabled or self.disabled_reason is not None:
            raise ValueError("reference nodes cannot be disabled")
        return self


LineLibraryNode: TypeAlias = Annotated[
    GroupNode | LineNode | ReferenceNode,
    Field(discriminator="kind"),
]


LineLibraryErrorCode: TypeAlias = Literal[
    "invalid_filter", "line_library_unavailable", "unexpected_failure"
]


class LineLibraryErrorResponse(ContractModel):
    code: LineLibraryErrorCode
    message: StrictStr


class LineLibraryResponse(ContractModel):
    roots: list[StrictStr] = Field(default_factory=list)
    nodes: dict[StrictStr, LineLibraryNode] = Field(default_factory=dict)
    filters: list[FilterDeclaration] = Field(default_factory=list)
    filter_apply_mode: Literal["immediate", "explicit"] = "immediate"
    sorts: list[SortDeclaration] = Field(default_factory=list)
    selection_limit: StrictInt | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_normalized_graph(self) -> "LineLibraryResponse":
        node_ids = set(self.nodes)
        if any(root not in node_ids for root in self.roots):
            raise ValueError("roots must address nodes")
        if len(set(self.roots)) != len(self.roots):
            raise ValueError("roots must be unique")
        for node_id, node in self.nodes.items():
            if node.id != node_id:
                raise ValueError("nodes must be keyed by each node's id")
            if any(child not in node_ids for child in node.child_ids):
                raise ValueError("child_ids must address nodes")
            if isinstance(node, ReferenceNode) and node.target_id not in node_ids:
                raise ValueError("reference target_id must address a node")
            if isinstance(node, ReferenceNode) and isinstance(
                self.nodes.get(node.target_id), ReferenceNode
            ):
                raise ValueError("references must target canonical nodes")
        self._validate_child_acyclic(node_ids)
        filter_keys = [declaration.key for declaration in self.filters]
        if len(set(filter_keys)) != len(filter_keys):
            raise ValueError("filter keys must be unique")
        sort_keys = [declaration.key for declaration in self.sorts]
        if len(set(sort_keys)) != len(sort_keys):
            raise ValueError("sort keys must be unique")
        if sum(declaration.default for declaration in self.sorts) > 1:
            raise ValueError("at most one sort may be default")
        return self

    def _validate_child_acyclic(self, node_ids: set[str]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                raise ValueError("normalized child graph must be acyclic")
            if node_id in visited:
                return
            visiting.add(node_id)
            for child_id in self.nodes[node_id].child_ids:
                visit(child_id)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in node_ids:
            visit(node_id)
