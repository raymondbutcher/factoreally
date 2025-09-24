"""Null hint for controlling null value generation."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import NULL, AnalysisHint


@dataclass(frozen=True, kw_only=True)
class NullHint(AnalysisHint):
    """Hint for null value control."""

    type: str = "NULL"

    pct: float

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through null hint - continue chain or return None."""
        # Use pct as probability (e.g., 20.0 means 20% chance of null value)
        if random.random() * 100 <= self.pct:
            return NULL
        return call_next(value)  # Continue the hint chain
