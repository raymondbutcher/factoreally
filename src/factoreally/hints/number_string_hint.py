"""Number string hint for generating numeric values as strings."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.number_hint import NumberHint


@dataclass(frozen=True, kw_only=True)
class NumberStringHint(NumberHint):
    """Hint for numeric values that should be generated as strings."""

    type: str = "NUMSTR"

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric string hint - generate number then convert to string."""

        # First generate a numeric value using parent logic
        value = super().process_value(value, call_next)

        # Convert numbers to string
        if isinstance(value, int | float):
            value = str(value)

        return value
