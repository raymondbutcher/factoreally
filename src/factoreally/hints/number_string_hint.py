"""Number string hint for generating numeric values as strings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from factoreally.hints.number_hint import NumberHint

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from factoreally.hints.base import AnalysisHint, SimpleType


@dataclass(frozen=True, kw_only=True)
class NumberStringHint(NumberHint):
    """Hint for numeric values that should be generated as strings."""

    type: str = "NUMSTR"

    @classmethod
    def create_from_values(cls, values: Sequence[SimpleType]) -> AnalysisHint | None:
        """Create NumberStringHint from sample values if they're all numeric digits."""

        numbers: list[int | float] = []

        for value in values:
            try:
                numbers.append(int(value))
            except ValueError:
                try:
                    numbers.append(float(value))
                except ValueError:
                    return None

        if number_hint := super().create_from_values(values):
            return cls(**asdict(number_hint))

        return None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric string hint - generate number then convert to string."""

        # First generate a numeric value using parent logic
        value = super().process_value(value, call_next)

        # Convert numbers to string
        if isinstance(value, int | float):
            value = str(value)

        return value
