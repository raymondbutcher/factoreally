"""Base classes for analyzers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections import Counter

    from factoreally.hints.base import SimpleType


class FieldValueCollector(ABC):
    """Analyzer that collects field values during data extraction."""

    @abstractmethod
    def collect_field_value(self, field: str, value: Any) -> None:
        """Collect information about a field value.

        Args:
            field: The field name
            value: The value to collect
        """
        ...


class FieldAnalyzer(ABC):
    """Analyzer that performs batch analysis on collected field data."""

    @abstractmethod
    def analyze_field(self, field: str) -> None:
        """Analyze all collected data for a field.

        Args:
            field: The field name to analyze
        """
        ...


class FieldValueCountsAnalyzer(ABC):
    """Analyzer that processes field value counts to generate hints."""

    @abstractmethod
    def analyze_field_value_counts(self, field: str, value_counts: Counter[SimpleType]) -> bool:
        """Analyze all values for a field across all items.

        Args:
            field: The field name to analyze
            value_counts: Counter of values and their occurrence counts

        Returns:
            True if analysis was successful/applicable, False otherwise
        """
        ...
