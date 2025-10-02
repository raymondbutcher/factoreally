"""Number hint for generating numeric values with various distributions."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, NamedTuple

from factoreally.hints.base import AnalysisHint


class NormalDistribution(NamedTuple):
    """Parameters for normal distribution."""

    mean: float
    std: float


class GammaDistribution(NamedTuple):
    """Parameters for gamma distribution."""

    alpha: float
    beta: float
    loc: float


@dataclass(frozen=True, kw_only=True)
class NumberHint(AnalysisHint):
    """Unified hint for numeric distribution generation."""

    type: str = "NUMBER"

    # Standard fields
    min: int | float
    max: int | float
    prec: int | None = None

    # Distribution parameters
    norm: NormalDistribution | None = None
    gamma: GammaDistribution | None = None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric hint - generate if no input, continue chain."""
        if value is None:
            if self.min == self.max:
                return self.min
            # Determine distribution type based on populated fields
            if self.norm is not None:
                # Normal distribution
                value = random.normalvariate(self.norm.mean, self.norm.std)
            elif self.gamma is not None:
                # Gamma distribution
                value = random.gammavariate(self.gamma.alpha, 1 / self.gamma.beta) + self.gamma.loc
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
