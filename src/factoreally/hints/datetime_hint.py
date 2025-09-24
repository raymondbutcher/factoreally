"""Datetime hint for generating datetime range values."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class DatetimeHint(AnalysisHint):
    """Hint for datetime range generation."""

    type: str = "DATETIME"

    min: str
    max: str

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
