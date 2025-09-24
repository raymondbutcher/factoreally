"""Duration range hint for generating realistic duration values."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class DurationRangeHint(AnalysisHint):
    """Hint for realistic duration generation."""

    type: str = "DURATION"

    fmt: str
    min: float
    max: float
    avg: float

    # TODO: add `prec: int | None` for precision and then round values

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through duration range hint - generate if no input, continue chain."""
        if value is None:
            # Use normal distribution centered on average for more realistic durations
            # Estimate standard deviation from range (assuming ~95% of values within range)
            range_width = self.max - self.min
            estimated_std = range_width / 6  # Rough estimate: ±3 std devs covers ~99.7%

            # Generate value using normal distribution centered on average
            seconds = random.normalvariate(self.avg, estimated_std)

            # Clamp to observed bounds to ensure realistic values
            seconds = max(self.min, min(self.max, seconds))

            # Convert to HMS format if format_type is specified
            if self.fmt == "HMS":
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds_remainder = seconds % 60

                # Format as HMS without microseconds to match expected pattern
                value = f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d}"
            elif self.fmt == "D.HMS.F":
                days = int(seconds // (24 * 3600))
                hours = int((seconds % (24 * 3600)) // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds_remainder = seconds % 60

                # Extract integer and fractional parts of seconds
                integer_seconds = int(seconds_remainder)
                fractional_part = seconds_remainder - integer_seconds

                # Format fractional part with up to 7 decimal places (like the example)
                fractional_str = f"{fractional_part:.7f}"[2:]  # Remove "0." prefix
                fractional_str = fractional_str.rstrip("0")  # Remove trailing zeros
                if not fractional_str:
                    fractional_str = "0"

                # Format as D.HMS.F to match expected pattern
                value = f"{days}.{hours:02d}:{minutes:02d}:{integer_seconds:02d}.{fractional_str}"
            elif self.fmt == "D.HMS":
                days = int(seconds // (24 * 3600))
                hours = int((seconds % (24 * 3600)) // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds_remainder = seconds % 60

                # Format as D.HMS without microseconds to match expected pattern
                value = f"{days}.{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d}"
            else:
                value = seconds
        return call_next(value)
