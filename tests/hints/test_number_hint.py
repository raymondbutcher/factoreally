"""Tests for array length generation using NumberHint."""

from factoreally.hints import NumberHint
from factoreally.hints.number_hint import (
    BetaDistribution,
    ExponentialDistribution,
    LognormDistribution,
    NormalDistribution,
    WeibullDistribution,
)


def test_number_hint_uniform_distribution_for_length() -> None:
    """Test NumberHint with uniform distribution for array length generation."""
    hint = NumberHint(min=2, max=5)

    def mock_call_next(value: int) -> int:
        return value

    # Test multiple generations
    results = []
    for _ in range(20):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be integers in the specified range
    assert all(isinstance(r, int) for r in results)
    assert all(2 <= r <= 5 for r in results)

    # Should have some variation (not all the same unless min == max)
    if hint.min != hint.max:
        assert len(set(results)) > 1


def test_number_hint_normal_distribution_for_length() -> None:
    """Test NumberHint with normal distribution for array length generation."""
    hint = NumberHint(min=1, max=10, norm=NormalDistribution(mean=5.0, std=2.0))

    def mock_call_next(value: int) -> int:
        return value

    # Test multiple generations
    results = []
    for _ in range(50):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be integers in the specified range
    assert all(isinstance(r, int) for r in results)
    assert all(1 <= r <= 10 for r in results)


def test_number_hint_constant_length() -> None:
    """Test NumberHint with constant length (min == max)."""
    hint = NumberHint(min=3, max=3)

    def mock_call_next(value: int) -> int:
        return value

    # Test multiple generations
    for _ in range(10):
        result = hint.process_value(None, mock_call_next)
        assert result == 3
        assert isinstance(result, int)


def test_number_hint_passes_existing_value() -> None:
    """Test that NumberHint passes through existing values unchanged."""
    hint = NumberHint(min=2, max=5)

    def mock_call_next(value: int) -> int:
        return value

    # Should pass through existing value
    result = hint.process_value(42, mock_call_next)
    assert result == 42


def test_number_hint_type_is_number() -> None:
    """Test that NumberHint has correct type."""
    hint = NumberHint(min=1, max=5)
    assert hint.type == "NUMBER"


def test_number_hint_beta_distribution() -> None:
    """Test NumberHint with beta distribution."""
    # Beta distribution with typical parameters, using prec to preserve float type
    hint = NumberHint(min=0.0, max=1.0, prec=2, beta=BetaDistribution(a=2.0, b=5.0, loc=0.0, scale=1.0))

    def mock_call_next(value: float) -> float:
        return value

    # Test multiple generations
    results = []
    for _ in range(50):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be floats in the specified range
    assert all(isinstance(r, float) for r in results)
    assert all(0.0 <= r <= 1.0 for r in results)

    # Should have some variation
    assert len(set(results)) > 1


def test_number_hint_lognorm_distribution() -> None:
    """Test NumberHint with log-normal distribution."""
    # Log-normal distribution with typical parameters, using prec to preserve float type
    hint = NumberHint(min=0.1, max=10.0, prec=2, lognorm=LognormDistribution(s=1.0, loc=0.0, scale=1.0))

    def mock_call_next(value: float) -> float:
        return value

    # Test multiple generations
    results = []
    for _ in range(50):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be floats in the specified range
    assert all(isinstance(r, float) for r in results)
    assert all(0.1 <= r <= 10.0 for r in results)

    # Should have some variation
    assert len(set(results)) > 1


def test_number_hint_expon_distribution() -> None:
    """Test NumberHint with exponential distribution."""
    # Exponential distribution with typical parameters, using prec to preserve float type
    hint = NumberHint(min=0.0, max=5.0, prec=2, expon=ExponentialDistribution(loc=0.0, scale=1.0))

    def mock_call_next(value: float) -> float:
        return value

    # Test multiple generations
    results = []
    for _ in range(50):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be floats in the specified range
    assert all(isinstance(r, float) for r in results)
    assert all(0.0 <= r <= 5.0 for r in results)

    # Should have some variation
    assert len(set(results)) > 1


def test_number_hint_weibull_distribution() -> None:
    """Test NumberHint with Weibull distribution."""
    # Weibull distribution with typical parameters, using prec to preserve float type
    hint = NumberHint(min=0.1, max=5.0, prec=2, weibull=WeibullDistribution(c=1.5, loc=0.0, scale=1.0))

    def mock_call_next(value: float) -> float:
        return value

    # Test multiple generations
    results = []
    for _ in range(50):
        result = hint.process_value(None, mock_call_next)
        results.append(result)

    # All results should be floats in the specified range
    assert all(isinstance(r, float) for r in results)
    assert all(0.1 <= r <= 5.0 for r in results)

    # Should have some variation
    assert len(set(results)) > 1
