"""Datetime hint for generating datetime range values."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class DatetimeHint(AnalysisHint):
    """Hint for datetime range generation."""

    type: str = "DATETIME"

    min: str
    max: str

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:  # noqa: C901
        """Create DatetimeHint from sample values if they match datetime patterns.

        Supports 7 datetime formats in priority order:
        1. ISO with mixed timezone (Z or +/-HH:MM)
        2. ISO Z with optional fractional seconds
        3. ISO with timezone and microseconds
        4. Unix seconds (10 digits)
        5. Unix milliseconds (13 digits)
        6. Space-separated datetime (YYYY-MM-DD HH:MM:SS)
        7. US datetime (MM/DD/YYYY HH:MM:SS)
        """

        def _parse_timestamp(value: str, format_str: str) -> datetime | None:
            """Parse timestamp string using the format string."""
            try:
                if format_str == "unix_seconds":
                    return datetime.fromtimestamp(int(value), tz=UTC)
                if format_str == "unix_milliseconds":
                    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)
                if format_str in ("iso_with_tz", "iso_with_tz_microseconds", "iso_z_mixed", "iso_mixed_tz"):
                    return datetime.fromisoformat(value)
                return datetime.strptime(value, format_str).replace(tzinfo=UTC)
            except (ValueError, KeyError):
                return None

        # Try each pattern in order
        patterns = [
            (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$", "iso_mixed_tz"),
            (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$", "iso_z_mixed"),
            (r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2}$", "iso_with_tz_microseconds"),
            (r"^\d{10}$", "unix_seconds"),
            (r"^\d{13}$", "unix_milliseconds"),
            (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", "%Y-%m-%d %H:%M:%S"),
            (r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$", "%m/%d/%Y %H:%M:%S"),
        ]

        for regex_pattern, format_str in patterns:
            if all(re.match(regex_pattern, v) for v in values):
                timestamps = []
                for value in values:
                    parsed = _parse_timestamp(value, format_str)
                    if parsed:
                        timestamps.append(parsed)

                if timestamps:
                    return cls(
                        min=min(timestamps).isoformat(),
                        max=max(timestamps).isoformat(),
                    )

        return None

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through datetime hint - generate if no input, continue chain."""
        if value is None:
            # Parse ISO format dates
            start_dt = datetime.fromisoformat(self.min)
            end_dt = datetime.fromisoformat(self.max)
            # Generate random timestamp between min and max
            random_ts = random.uniform(start_dt.timestamp(), end_dt.timestamp())
            value = datetime.fromtimestamp(random_ts, start_dt.tzinfo).isoformat()

        return call_next(value)
