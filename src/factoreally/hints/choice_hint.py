"""Choice hint for generating categorical values with optional weighting."""

import random
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self

from factoreally.constants import MAX_PRECISION
from factoreally.hints.base import AnalysisHint, SimpleType


@dataclass(frozen=True, kw_only=True)
class ChoiceHint(AnalysisHint):
    """Hint for choice generation with optional weighting."""

    type: str = "CHOICE"

    choices: list[SimpleType]
    weights: list[float] | None = None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through choice hint - generate if no input, continue chain."""
        if value is None and self.choices:
            if self.weights and len(self.choices) == len(self.weights):
                # Use weighted choice when weights are provided
                value = random.choices(self.choices, weights=self.weights)[0]
            else:
                # Use simple uniform choice when no weights or mismatched lengths
                value = random.choice(self.choices)
        return call_next(value)

    @classmethod
    def create(cls, field_value_counts: Counter[Any]) -> Self:
        """Generate structured hint for choice field factory generation."""

        if len(field_value_counts) < 2:  # noqa: PLR2004
            msg = "needs 2 values for a choice"
            raise ValueError(msg)

        total_value_count = sum(field_value_counts.values())
        value_weights = {value: count / total_value_count for value, count in field_value_counts.items()}
        sorted_value_weights = sorted(value_weights.items(), key=lambda x: x[1], reverse=True)

        return cls(
            choices=[value for value, _ in sorted_value_weights],
            weights=[round(weight, MAX_PRECISION) for _, weight in sorted_value_weights],
        )
