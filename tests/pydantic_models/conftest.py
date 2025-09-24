"""Shared fixtures and models for pydantic model tests."""

from typing import Any

from pydantic import BaseModel


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
