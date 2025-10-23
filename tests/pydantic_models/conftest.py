"""Shared fixtures and models for pydantic model tests."""

from collections.abc import Mapping
from datetime import date
from typing import Any

from pydantic import BaseModel, RootModel


class SimpleModel(BaseModel):
    name: str
    age: int
    metadata: dict[str, Any]  # Dynamic field


class NestedModel(BaseModel):
    user_data: dict[str, str]  # Dynamic field
    settings: "ConfigModel"


class ConfigModel(BaseModel):
    theme: str
    preferences: dict[str, int]  # Dynamic field


class NoMetadataModel(BaseModel):
    name: str
    age: int
    tags: list[str]  # Not a dynamic dict


class DeepNestedModel(BaseModel):
    level1: "Level1Model"


class Level1Model(BaseModel):
    level2: "Level2Model"
    metadata: dict[str, str]  # Dynamic field at level 1


class Level2Model(BaseModel):
    name: str
    config: dict[str, Any]  # Dynamic field at level 2


# RootModel test classes using Mapping types
class DailyCounts(RootModel[Mapping[date, int]]):
    """Dictionary with date strings as keys and counts as values"""

    root: Mapping[date, int]


class MappingModel(BaseModel):
    """Model with a RootModel field using Mapping type."""

    name: str
    daily_stats: DailyCounts  # Dynamic field using RootModel with Mapping
