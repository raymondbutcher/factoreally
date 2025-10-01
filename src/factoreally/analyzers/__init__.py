"""Analysis orchestration for sample data analysis.

This module contains the core analysis logic that coordinates multiple specialized
analyzers to perform analysis of sample data.
"""

from __future__ import annotations

from factoreally.analyzers.array_analyzer import ArrayAnalyzer
from factoreally.analyzers.choice_analyzer import ChoiceAnalyzer
from factoreally.analyzers.null_analyzer import NullAnalyzer
from factoreally.analyzers.number_analyzer import NumericAnalyzer
from factoreally.analyzers.object_analyzer import ObjectAnalyzer
from factoreally.analyzers.presence_analyzer import PresenceAnalyzer
from factoreally.analyzers.string_pattern_analyzer import StringPatternAnalyzer


class Analyzers:
    """Container for all configured analyzers after analysis is complete."""

    def __init__(self) -> None:
        """Initialize all analyzers, passing self as the Analyzers instance."""
        self.array_analyzer = ArrayAnalyzer(self)
        self.choice_analyzer = ChoiceAnalyzer(self)
        self.null_analyzer = NullAnalyzer(self)
        self.numeric_analyzer = NumericAnalyzer(self)
        self.object_analyzer = ObjectAnalyzer(self)
        self.presence_analyzer = PresenceAnalyzer(self)
        self.string_pattern_analyzer = StringPatternAnalyzer(self)
