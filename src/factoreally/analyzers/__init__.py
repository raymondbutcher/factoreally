"""Analysis orchestration for sample data analysis.

This module contains the core analysis logic that coordinates multiple specialized
analyzers to perform analysis of sample data.
"""

from dataclasses import dataclass, field

from factoreally.analyzers.alphanumeric_analyzer import AlphanumericAnalyzer
from factoreally.analyzers.array_analyzer import ArrayAnalyzer
from factoreally.analyzers.choice_analyzer import ChoiceAnalyzer
from factoreally.analyzers.null_analyzer import NullAnalyzer
from factoreally.analyzers.number_analyzer import NumericAnalyzer
from factoreally.analyzers.object_analyzer import ObjectAnalyzer
from factoreally.analyzers.presence_analyzer import PresenceAnalyzer
from factoreally.analyzers.string_pattern_analyzer import StringPatternAnalyzer


@dataclass
class Analyzers:
    """Container for all configured analyzers after analysis is complete."""

    alphanumeric_analyzer: AlphanumericAnalyzer = field(default_factory=AlphanumericAnalyzer)
    array_analyzer: ArrayAnalyzer = field(default_factory=ArrayAnalyzer)
    choice_analyzer: ChoiceAnalyzer = field(default_factory=ChoiceAnalyzer)
    null_analyzer: NullAnalyzer = field(default_factory=NullAnalyzer)
    numeric_analyzer: NumericAnalyzer = field(default_factory=NumericAnalyzer)
    object_analyzer: ObjectAnalyzer = field(default_factory=ObjectAnalyzer)
    presence_analyzer: PresenceAnalyzer = field(default_factory=PresenceAnalyzer)
    string_pattern_analyzer: StringPatternAnalyzer = field(default_factory=StringPatternAnalyzer)
