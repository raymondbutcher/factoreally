"""Tests for Factory interface methods (copy, slice, iteration)."""

import itertools

import pytest

from factoreally import Factory


def test_init_with_overrides(simple_factory_spec: Factory) -> None:
    """Test Factory.__init__ with keyword override arguments."""
    base_factory = simple_factory_spec

    # Create factory with overrides using copy method
    factory_with_overrides = base_factory.copy(id="fixed-id", name="fixed-name", data__count=42)

    # Generate data
    data1 = base_factory.build()
    data2 = factory_with_overrides.build()

    # Verify overrides work
    assert data2["id"] == "fixed-id"
    assert data2["name"] == "fixed-name"
    assert data2["data"]["count"] == 42

    # Verify non-overridden factory generates different values
    assert data1["id"] != "fixed-id" or data1["name"] != "fixed-name"


def test_copy(simple_factory_spec: Factory) -> None:
    """Test Factory.copy method."""
    factory = simple_factory_spec

    # Create copy with overrides
    factory_copy = factory.copy(id="copy-id", data__count=333)

    # Generate data from both factories
    original_data = factory.build()
    copy_data = factory_copy.build()

    # Verify copy has overrides
    assert copy_data["id"] == "copy-id"
    assert copy_data["data"]["count"] == 333

    # Verify original is unchanged
    assert original_data["id"] != "copy-id"
    assert original_data["data"]["count"] != 333


def test_copy_with_base_overrides(simple_factory_spec: Factory) -> None:
    """Test Factory.copy preserves base overrides."""
    # Create factory with base overrides
    base_factory = simple_factory_spec
    factory = base_factory.copy(name="base-name")

    # Create copy with additional overrides
    factory_copy = factory.copy(id="copy-id")

    # Generate data from copy
    copy_data = factory_copy.build()

    # Verify both base and copy overrides are present
    assert copy_data["name"] == "base-name"  # Base override
    assert copy_data["id"] == "copy-id"  # Copy override


def test_slice_interface(simple_factory_spec: Factory) -> None:
    """Test Factory slice interface."""
    factory = simple_factory_spec

    # Test [:10] generates 10 items
    data_list = factory[:10]
    assert isinstance(data_list, list)
    assert len(data_list) == 10
    assert all(isinstance(data, dict) for data in data_list)

    # Test [0:10] generates 10 items
    data_list = factory[0:10]
    assert isinstance(data_list, list)
    assert len(data_list) == 10
    assert all(isinstance(data, dict) for data in data_list)

    # Test empty slice
    empty_list = factory[5:5]
    assert empty_list == []

    # Test slice with step
    data_list = factory[0:6:2]  # Should generate items at indices 0, 2, 4
    assert isinstance(data_list, list)
    assert len(data_list) == 3
    assert all(isinstance(data, dict) for data in data_list)


def test_slice_interface_edge_cases(simple_factory_spec: Factory) -> None:
    """Test Factory slice interface edge cases."""
    factory = simple_factory_spec

    # Test that slice without stop value raises error
    with pytest.raises(TypeError, match="Slice stop value is required"):
        factory[10:]

    # Test that slice without stop value raises error
    with pytest.raises(TypeError, match="Slice stop value is required"):
        factory[:]

    # Test integer index raises error
    with pytest.raises(TypeError, match="Only slice indexing is supported"):
        factory[0]

    # Test negative index raises error
    with pytest.raises(TypeError, match="Only slice indexing is supported"):
        factory[-1]

    # Test invalid key type raises error
    with pytest.raises(TypeError, match="Only slice indexing is supported"):
        factory["invalid"]


def test_iter_interface(simple_factory_spec: Factory) -> None:
    """Test Factory iteration interface."""
    factory = simple_factory_spec

    # Test that factory is iterable
    iterator = iter(factory)
    assert iterator is factory  # Returns self

    # Test generating values from iterator
    data_list = []
    for i, data in enumerate(factory):
        data_list.append(data)
        if i >= 4:  # Generate 5 items
            break

    assert len(data_list) == 5
    assert all(isinstance(data, dict) for data in data_list)
    assert all("id" in data for data in data_list)

    # Test with itertools.islice
    islice_data = list(itertools.islice(factory, 3))
    assert len(islice_data) == 3
    assert all(isinstance(data, dict) for data in islice_data)
    assert all("id" in data for data in islice_data)

    # Test direct iteration with for loop
    direct_iter_data = []
    for data in factory:
        direct_iter_data.append(data)
        if len(direct_iter_data) >= 2:  # Generate 2 items
            break

    assert len(direct_iter_data) == 2
    assert all(isinstance(data, dict) for data in direct_iter_data)
    assert all("id" in data for data in direct_iter_data)
