"""Number string hint for generating numeric values as strings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.number_hint import NumberHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class NumberStringHint(NumberHint):
    """Hint for numeric values that should be generated as strings."""

    type: str = "NUMSTR"

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create NumberStringHint from sample values if they're all numeric digits."""
        if not all(v.isdigit() for v in values):
            return None
        numeric_values = [float(v) for v in values]
        return cls(min=min(numeric_values), max=max(numeric_values))

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric string hint - generate number then convert to string."""

        # First generate a numeric value using parent logic
        value = super().process_value(value, call_next)

        # Convert numbers to string
        if isinstance(value, int | float):
            value = str(value)

        return value
