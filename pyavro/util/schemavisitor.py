from enum import Enum
from typing import Protocol, TypeVar
from __future__ import annotations

from pyavro.schema import Schema

T = TypeVar("T", covariant=True)


class SchemaVisitor(Protocol[T]):
    def visit_terminal(self, terminal: Schema) -> SchemaVisitorAction:
        ...

    def visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        ...

    def after_visit_non_terminal(self, non_terminal: Schema) -> SchemaVisitorAction:
        ...

    def get(self) -> T:
        ...

class SchemaVisitorAction(Enum):
    CONTINUE = "CONTINUE"
    TERMINATE = "TERMINATE"
    SKIP_SUBTREE = "SKIP_SUBTREE"
    SKIP_SIBLINGS = "SKIP_SIBLINGS"