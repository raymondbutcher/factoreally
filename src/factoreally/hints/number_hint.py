"""Number hint for generating numeric values with various distributions."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class NumberHint(AnalysisHint):
    """Unified hint for numeric distribution generation."""

    type: str = "NUMBER"

    # Required fields
    min: int | float
    max: int | float

    # Optional fields for normal distribution
    mean: float | None = None
    std: float | None = None

    # Optional fields for gamma distribution
    alpha: float | None = None
    beta: float | None = None
    loc: float | None = None

    # Optional field for precision
    prec: int | None = None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric hint - generate if no input, continue chain."""
        if value is None:
            if self.min == self.max:
                return self.min
            # Determine distribution type based on populated fields
            if self.mean is not None and self.std is not None:
                # Normal distribution
                value = random.normalvariate(self.mean, self.std)
            elif self.alpha is not None and self.beta is not None and self.loc is not None:
                # Gamma distribution
                value = random.gammavariate(self.alpha, 1 / self.beta) + self.loc
            # Uniform distribution
            elif isinstance(self.min, int) and isinstance(self.max, int):
                value = random.randint(int(self.min), int(self.max))
            else:
                value = random.uniform(float(self.min), float(self.max))

            # Clamp the upper and lower limits
            value = max(self.min, min(self.max, value))

            # Apply precision rounding
            value = round(value, self.prec)

        return call_next(value)
