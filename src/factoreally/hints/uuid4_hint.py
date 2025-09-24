"""UUID4 hint for generating UUID version 4 identifiers."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class Uuid4Hint(AnalysisHint):
    """Hint for UUID4 pattern generation."""

    type: str = "UUID4"

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through UUID4 hint - generate UUID if no input, continue chain."""
        if value is None:
            value = str(uuid.uuid4())
        return call_next(value)
