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


class BetaDistribution(NamedTuple):
    """Parameters for beta distribution."""

    a: float
    b: float
    loc: float
    scale: float


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
    beta: BetaDistribution | None = None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric hint - generate if no input, continue chain."""
        if value is None:
            if self.min == self.max:
                return self.min

            if self.norm is not None:
                value = random.normalvariate(self.norm.mean, self.norm.std)
            elif self.gamma is not None:
                value = random.gammavariate(self.gamma.alpha, 1 / self.gamma.beta) + self.gamma.loc
            elif self.beta is not None:
                value = self.beta.loc + self.beta.scale * random.betavariate(self.beta.a, self.beta.b)
            elif isinstance(self.min, int) and isinstance(self.max, int):
                value = random.randint(int(self.min), int(self.max))
            else:
                value = random.uniform(float(self.min), float(self.max))

            # Clamp the upper and lower limits
            value = max(self.min, min(self.max, value))

            # Apply precision rounding
            value = round(value, self.prec)

        return call_next(value)
