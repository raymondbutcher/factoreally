"""Date hint for generating ISO date strings."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any, Self

from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, kw_only=True)
class DateHint(AnalysisHint):
    """Hint for date pattern generation (YYYY-MM-DD format)."""

    type: str = "DATE"

    min: str  # Minimum date in YYYY-MM-DD format
    max: str  # Maximum date in YYYY-MM-DD format

    @classmethod
    def create_from_values(cls, values: list[str]) -> Self | None:
        """Create DateHint from sample values if they match date pattern."""
        if not all(re.match(r"^\d{4}-\d{2}-\d{2}$", v) for v in values):
            return None
        return cls(min=min(values), max=max(values))

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
