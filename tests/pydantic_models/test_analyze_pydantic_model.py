"""Tests for analyze_pydantic_model function."""

from factoreally.pydantic_models import analyze_pydantic_model

from .conftest import (
    DailyCounts,
    DeepNestedModel,
    MappingModel,
    NestedModel,
    NoMetadataModel,
    SimpleModel,
)


def test_analyze_pydantic_model_simple() -> None:
    """Test analyzing a simple model with one dynamic dict field."""
    dynamic_fields = analyze_pydantic_model(SimpleModel)

    assert "metadata" in dynamic_fields
    assert "name" not in dynamic_fields
    assert "age" not in dynamic_fields
    assert len(dynamic_fields) == 1


def test_analyze_pydantic_model_nested() -> None:
    """Test analyzing nested models with dynamic dict fields."""
    dynamic_fields = analyze_pydantic_model(NestedModel)

    assert "user_data" in dynamic_fields
    assert "settings.preferences" in dynamic_fields
    assert "settings" not in dynamic_fields
    assert "settings.theme" not in dynamic_fields
    assert len(dynamic_fields) == 2


def test_analyze_pydantic_model_no_metadata() -> None:
    """Test analyzing a model with no dynamic dict fields."""
    dynamic_fields = analyze_pydantic_model(NoMetadataModel)

    assert len(dynamic_fields) == 0
    assert "name" not in dynamic_fields
    assert "age" not in dynamic_fields
    assert "tags" not in dynamic_fields


def test_analyze_pydantic_model_deep_nested() -> None:
    """Test analyzing deeply nested models."""
    dynamic_fields = analyze_pydantic_model(DeepNestedModel)

    expected_fields = {"level1.metadata", "level1.level2.config"}

    assert dynamic_fields == expected_fields
    assert len(dynamic_fields) == 2


def test_analyze_pydantic_model_rootmodel_with_mapping() -> None:
    """Test analyzing RootModel with Mapping type."""
    dynamic_fields = analyze_pydantic_model(DailyCounts)

    # RootModel fields are exposed at the root level, so we expect "root" to be detected
    assert "root" in dynamic_fields
    assert len(dynamic_fields) == 1


def test_analyze_pydantic_model_with_mapping_field() -> None:
    """Test analyzing a model containing a RootModel[Mapping[...]] field."""
    dynamic_fields = analyze_pydantic_model(MappingModel)

    # Should detect both the RootModel field and its root attribute
    assert "daily_stats" in dynamic_fields
    assert "daily_stats.root" in dynamic_fields
    assert "name" not in dynamic_fields
    assert len(dynamic_fields) == 2
