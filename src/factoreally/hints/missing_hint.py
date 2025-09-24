"""Missing hint for controlling field presence."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import MISSING, AnalysisHint


@dataclass(frozen=True, kw_only=True)
class MissingHint(AnalysisHint):
    """Hint for field presence control."""

    type: str = "MISSING"

    pct: float

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through missing hint - continue chain or return MISSING."""
        # Use pct as probability (e.g., 70.0 means 70% chance of field being present)
        if random.random() * 100 > self.pct:
            return MISSING
        return call_next(value)  # Continue the hint chain
