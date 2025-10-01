"""Duration range hint for generating realistic duration values."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from factoreally.constants import MAX_PRECISION
from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class DurationRangeHint(AnalysisHint):
    """Hint for realistic duration generation."""

    type: str = "DURATION"

    fmt: str
    min: float
    max: float
    avg: float

    # TODO: add `prec: int | None` for precision and then round values

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:  # noqa: C901, PLR0912, PLR0915
        """Create DurationRangeHint from sample values if they match duration patterns.

        Supports 3 duration format groups:
        1. HMS/D.HMS/D.HMS.F - Flexible time format with optional days and fractional seconds
        2. ISO8601 Days (P#D)
        3. ISO8601 Weeks (P#W)
        """

        def _parse_hms_duration(value: str) -> float | None:
            """Parse HMS duration format."""
            hms_match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})$", value)
            if hms_match:
                hours, minutes, seconds = map(int, hms_match.groups())
                return hours * 3600 + minutes * 60 + seconds
            return None

        def _parse_dhms_fractional_duration(value: str) -> float | None:
            """Parse D.HMS.F duration format with fractional seconds."""
            dhms_fractional_match = re.match(r"^(\d+\.)?(\d{1,2}):(\d{2}):(\d{2})\.(\d+)$", value)
            if dhms_fractional_match:
                days_str, hours_str, minutes_str, seconds_str, fractional_str = dhms_fractional_match.groups()
                days, hours, minutes, seconds = (
                    int(days_str.removesuffix(".") if days_str else 0),
                    int(hours_str),
                    int(minutes_str),
                    int(seconds_str),
                )
                fractional_seconds = float(f"0.{fractional_str}")
                return days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds + fractional_seconds
            return None

        def _parse_dhms_duration(value: str) -> float | None:
            """Parse D.HMS duration format."""
            dhms_match = re.match(r"^(\d+)\.(\d{1,2}):(\d{2}):(\d{2})$", value)
            if dhms_match:
                days, hours, minutes, seconds = map(int, dhms_match.groups())
                return days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds
            return None

        def _parse_iso8601_duration(value: str, unit: str) -> float | None:
            """Parse ISO8601 duration format."""
            match = re.search(r"\d+", value)
            if match:
                amount = int(match.group())
                if unit == "days":
                    return amount * 24 * 3600
                if unit == "weeks":
                    return amount * 7 * 24 * 3600
            return None

        def _parse_duration_seconds(value: str, pattern_format: str) -> float | None:
            """Parse duration value and return seconds."""
            try:
                if pattern_format == "HMS":
                    return _parse_hms_duration(value)
                if pattern_format == "D.HMS.F":
                    return _parse_dhms_fractional_duration(value)
                if pattern_format == "D.HMS":
                    return _parse_dhms_duration(value)
                if pattern_format == "ISO8601_Days":
                    return _parse_iso8601_duration(value, "days")
                if pattern_format == "ISO8601_Weeks":
                    return _parse_iso8601_duration(value, "weeks")
            except ValueError:
                pass
            return None

        # Try ISO8601 weeks first (most specific)
        if all(re.match(r"^P\d+W$", v) for v in values):
            durations = []
            for value in values:
                duration_seconds = _parse_duration_seconds(value, "ISO8601_Weeks")
                if duration_seconds is not None:
                    durations.append(duration_seconds)
            if durations:
                return cls(
                    min=min(durations),
                    max=max(durations),
                    avg=round(sum(durations) / len(durations), MAX_PRECISION),
                    fmt="ISO8601_Weeks",
                )

        # Try ISO8601 days
        if all(re.match(r"^P\d+D$", v) for v in values):
            durations = []
            for value in values:
                duration_seconds = _parse_duration_seconds(value, "ISO8601_Days")
                if duration_seconds is not None:
                    durations.append(duration_seconds)
            if durations:
                return cls(
                    min=min(durations),
                    max=max(durations),
                    avg=round(sum(durations) / len(durations), MAX_PRECISION),
                    fmt="ISO8601_Days",
                )

        # Try HMS/D.HMS/D.HMS.F (flexible pattern)
        pattern = r"^(\d+\.)?(\d{1,2}):(\d{2}):(\d{2})(\.(\d+))?$"
        if all(re.match(pattern, v) for v in values):
            has_days = False
            has_fractional = False

            for value in values:
                match = re.match(pattern, value)
                if match:
                    if match.group(1):  # days component
                        has_days = True
                    if match.group(5):  # fractional component (with dot)
                        has_fractional = True

            # Determine format
            if has_days and has_fractional:
                fmt = "D.HMS.F"
            elif has_days:
                fmt = "D.HMS"
            else:
                fmt = "HMS"

            # Parse all durations using the determined format
            durations = []
            for value in values:
                duration_seconds = _parse_duration_seconds(value, fmt)
                if duration_seconds is not None:
                    durations.append(duration_seconds)

            if durations:
                return cls(
                    min=min(durations),
                    max=max(durations),
                    avg=round(sum(durations) / len(durations), MAX_PRECISION),
                    fmt=fmt,
                )

        return None

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
