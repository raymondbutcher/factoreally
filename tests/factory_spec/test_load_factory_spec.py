"""Tests for load_factory_spec function."""

from factoreally.factory_spec import FactorySpec, load_factory_spec


def test_load_factory_spec_from_dict() -> None:
    """Test loading FactorySpec from dictionary."""
    spec_dict = {
        "metadata": {"generated": "2024-01-01"},
        "fields": {
            "name": {"CONST": {"val": "test"}},
            "status": {"CHOICE": {"choices": ["active", "inactive"], "weights": [70, 30]}},
        },
    }

    factory_spec = load_factory_spec(spec_dict)

    assert isinstance(factory_spec, FactorySpec)


def test_load_factory_spec_with_metadata() -> None:
    """Test loading FactorySpec from dictionary with metadata."""
    spec_dict = {
        "metadata": {"generated": "2024-01-01", "samples_analyzed": 100, "unique_fields": 2},
        "fields": {
            "id": {"CONST": {"val": 1}},
            "name": {"CONST": {"val": "test_user"}},
        },
    }

    factory_spec = load_factory_spec(spec_dict)

    assert isinstance(factory_spec, FactorySpec)
    result = factory_spec.build()
    assert result == {"id": 1, "name": "test_user"}
