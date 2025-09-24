"""Date hint for generating ISO date strings."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class DateHint(AnalysisHint):
    """Hint for date pattern generation (YYYY-MM-DD format)."""

    type: str = "DATE"

    min: str  # Minimum date in YYYY-MM-DD format
    max: str  # Maximum date in YYYY-MM-DD format

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through date hint - generate if no input, continue chain."""
        if value is None:
            # Generate a date in YYYY-MM-DD format
            # Parse min and max dates
            min_date = date.fromisoformat(self.min)
            max_date = date.fromisoformat(self.max)

            # Generate random timestamp between min and max
            time_delta = max_date - min_date
            random_days = random.randint(0, time_delta.days)
            random_date = min_date + timedelta(days=random_days)
            value = random_date.strftime("%Y-%m-%d")
        return call_next(value)
