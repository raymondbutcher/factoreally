"""Auth0 ID hint for generating Auth0 identifier patterns."""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from factoreally.hints.base import AnalysisHint


@dataclass(frozen=True, kw_only=True)
class Auth0IdHint(AnalysisHint):
    """Hint for Auth0 ID pattern generation."""

    type: str = "AUTH0_ID"

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through Auth0 ID hint - generate if no input, continue chain."""
        if value is None:
            hex_string = "".join(random.choice("0123456789abcdef") for _ in range(24))
            value = f"auth0|{hex_string}"
        return call_next(value)
