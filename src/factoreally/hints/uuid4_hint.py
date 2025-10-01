"""UUID4 hint for generating UUID version 4 identifiers."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class Uuid4Hint(AnalysisHint):
    """Hint for UUID4 pattern generation."""

    type: str = "UUID4"

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create Uuid4Hint from sample values if they match UUID pattern."""
        if not all(
            re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v.lower()) for v in values
        ):
            return None
        return cls()

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through UUID4 hint - generate UUID if no input, continue chain."""
        if value is None:
            value = str(uuid.uuid4())
        return call_next(value)
