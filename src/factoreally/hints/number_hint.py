"""Number hint for generating numeric values with various distributions."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple, cast, get_args, get_type_hints

import numpy as np
from scipy import stats

from factoreally.constants import MAX_PRECISION
from factoreally.hints.base import AnalysisHint

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from factoreally.hints.base import SimpleType

# Distribution fitting constants
KS_TEST_P_VALUE_THRESHOLD = 0.05
MIN_SAMPLES_UNIFORM = 6
MIN_SAMPLES_EXPONENTIAL = 10
MIN_SAMPLES_BETA = 12
MIN_SAMPLES_NORMAL = 15
MIN_SAMPLES_LOGNORM = 15
MIN_SAMPLES_WEIBULL = 18
MIN_SAMPLES_GAMMA = 20


class NormalDistribution(NamedTuple):
    """Parameters for normal distribution."""

    mean: float
    std: float


class GammaDistribution(NamedTuple):
    """Parameters for gamma distribution."""

    alpha: float
    beta: float
    loc: float


class BetaDistribution(NamedTuple):
    """Parameters for beta distribution."""

    a: float
    b: float
    loc: float
    scale: float


class LognormDistribution(NamedTuple):
    """Parameters for log-normal distribution."""

    s: float
    loc: float
    scale: float


class ExponentialDistribution(NamedTuple):
    """Parameters for exponential distribution."""

    loc: float
    scale: float


class WeibullDistribution(NamedTuple):
    """Parameters for Weibull distribution."""

    c: float
    loc: float
    scale: float


class OutlierResult(NamedTuple):
    """Minimal outlier detection result."""

    data_without_extreme_outliers: np.ndarray
    iqr_lower: float
    iqr_upper: float


@dataclass(frozen=True, kw_only=True)
class NumberHint(AnalysisHint):
    """Unified hint for numeric distribution generation."""

    type: str = "NUMBER"

    # Standard fields
    min: int | float
    max: int | float
    prec: int | None = None

    # Distribution parameters
    norm: NormalDistribution | None = None
    gamma: GammaDistribution | None = None
    beta: BetaDistribution | None = None
    lognorm: LognormDistribution | None = None
    expon: ExponentialDistribution | None = None
    weibull: WeibullDistribution | None = None

    def __post_init__(self) -> None:
        """Convert list arguments to NamedTuple instances for distribution parameters."""
        for field_name, field_type in get_type_hints(self.__class__).items():
            value = getattr(self, field_name)
            if isinstance(value, list):
                for arg in get_args(field_type):
                    if isinstance(arg, type) and issubclass(arg, tuple):
                        object.__setattr__(self, field_name, arg(*value))
                        break

    @classmethod
    def create_from_values(cls, values: Sequence[SimpleType]) -> AnalysisHint | None:
        """Create a NumberHint from a list of values by analyzing their distribution.

        Args:
            values: List of numeric values to analyze

        Returns:
            NumberHint instance configured for the detected distribution, or None if analysis fails
        """
        if not values:
            return None

        is_integer = True
        for value in values:
            if type(value) is int:
                pass
            elif type(value) is float:
                is_integer = False
            else:
                return None

        values = cast("Sequence[int | float]", values)

        precision = None if is_integer else _calculate_precision(values)  # type: ignore[arg-type]

        if len(set(values)) == 1:
            return NumberHint(min=values[0], max=values[0])

        if hint := _get_best_distribution_hint(values, precision):
            return hint

        return NumberHint(
            min=round(min(values), precision),
            max=round(max(values), precision),
            prec=precision,
        )

    def process_value(self, value: Any, call_next: Callable[[Any], Any]) -> Any:
        """Process value through numeric hint - generate if no input, continue chain."""
        if value is None:
            if self.min == self.max:
                return self.min

            if self.norm is not None:
                value = random.normalvariate(self.norm.mean, self.norm.std)
            elif self.gamma is not None:
                value = random.gammavariate(self.gamma.alpha, 1 / self.gamma.beta) + self.gamma.loc
            elif self.beta is not None:
                value = self.beta.loc + self.beta.scale * random.betavariate(self.beta.a, self.beta.b)
            elif self.lognorm is not None:
                mu = math.log(self.lognorm.scale) if self.lognorm.scale > 0 else 0
                value = random.lognormvariate(mu, self.lognorm.s) + self.lognorm.loc
            elif self.expon is not None:
                lambd = 1 / self.expon.scale if self.expon.scale > 0 else 1
                value = random.expovariate(lambd) + self.expon.loc
            elif self.weibull is not None:
                value = random.weibullvariate(self.weibull.scale, self.weibull.c) + self.weibull.loc
            elif isinstance(self.min, int) and isinstance(self.max, int):
                value = random.randint(int(self.min), int(self.max))
            else:
                value = random.uniform(float(self.min), float(self.max))

            # Clamp the upper and lower limits
            value = max(self.min, min(self.max, value))

            # Apply precision rounding
            value = round(value, self.prec)

        return call_next(value)


def _calculate_precision(values: list[int | float]) -> int | None:
    """Calculate the suitable precision level for float values.

    Args:
        values: List of numeric values

    Returns:
        Precision level (number of decimal places) for float values, or None for integers
    """
    # Check if all values are integers
    if all(isinstance(v, int) for v in values):
        return None

    # For float values, find the maximum number of decimal places in the sample data
    max_precision = 0
    for value in values:
        if isinstance(value, float):
            # Convert to string and count decimal places
            str_val = str(value)
            if "." in str_val:
                decimal_part = str_val.split(".")[1].rstrip("0")  # Remove trailing zeros
                max_precision = max(max_precision, len(decimal_part))

    # Cap precision at a reasonable level to avoid extremely long decimals
    return min(max_precision, 6)


def _detect_outliers(data: np.ndarray) -> OutlierResult:
    """Detect and remove extreme outliers using IQR method."""
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1

    # IQR bounds for min/max values
    iqr_lower = q1 - 1.5 * iqr
    iqr_upper = q3 + 1.5 * iqr

    # Extreme outliers (3 * IQR) - remove these from fitting data
    extreme_lower = q1 - 3 * iqr
    extreme_upper = q3 + 3 * iqr
    extreme_outliers = (data < extreme_lower) | (data > extreme_upper)

    return OutlierResult(
        data_without_extreme_outliers=data[~extreme_outliers],
        iqr_lower=float(iqr_lower),
        iqr_upper=float(iqr_upper),
    )


def _try_normal_distribution(
    data: np.ndarray,
    data_min: float,  # noqa: ARG001
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting normal distribution."""
    # Normal distribution needs sufficient data to estimate mean and std reliably
    if len(data) < MIN_SAMPLES_NORMAL:
        return (None, 0.0)

    try:
        params = stats.norm.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.norm.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        mean, std = params
        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            norm=NormalDistribution(mean=round(mean, MAX_PRECISION), std=round(std, MAX_PRECISION)),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_uniform_distribution(
    data: np.ndarray,
    data_min: float,  # noqa: ARG001
    outliers: OutlierResult,  # noqa: ARG001
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting uniform distribution."""
    # Uniform distribution needs enough data to distinguish from other patterns
    if len(data) < MIN_SAMPLES_UNIFORM:
        return (None, 0.0)

    try:
        params = stats.uniform.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.uniform.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        loc, scale = params
        min_val = round(loc, precision)
        max_val = round(loc + scale, precision)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_gamma_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting gamma distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Gamma distribution has 3 parameters and requires substantial data for reliable fitting
    if len(data) < MIN_SAMPLES_GAMMA:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.gamma.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.gamma.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        alpha, loc, scale = params
        beta = 1 / scale if scale != 0 else 1
        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            gamma=GammaDistribution(
                alpha=round(alpha, MAX_PRECISION),
                beta=round(beta, MAX_PRECISION),
                loc=round(loc, MAX_PRECISION),
            ),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_beta_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting beta distribution. Returns (None, 0.0) if data not in [0,1] range."""
    # Beta distribution has 2 shape parameters requiring sufficient data for reliable estimation
    if len(data) < MIN_SAMPLES_BETA:
        return (None, 0.0)

    data_max = float(np.max(data))
    if not (data_min >= 0 and data_max <= 1):
        return (None, 0.0)

    try:
        params = stats.beta.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.beta.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        # Beta distribution uses IQR bounds from outlier analysis
        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        a, b, loc, scale = params

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            beta=BetaDistribution(
                a=round(a, MAX_PRECISION),
                b=round(b, MAX_PRECISION),
                loc=round(loc, MAX_PRECISION),
                scale=round(scale, MAX_PRECISION),
            ),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_lognorm_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting log-normal distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Log-normal distribution needs sufficient data to verify log-normality pattern
    if len(data) < MIN_SAMPLES_LOGNORM:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.lognorm.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.lognorm.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        s, loc, scale = params

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            lognorm=LognormDistribution(
                s=round(s, MAX_PRECISION),
                loc=round(loc, MAX_PRECISION),
                scale=round(scale, MAX_PRECISION),
            ),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_exponential_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting exponential distribution. Returns (None, 0.0) if data contains negative values."""
    # Exponential distribution needs sufficient data to verify exponential decay pattern
    if len(data) < MIN_SAMPLES_EXPONENTIAL:
        return (None, 0.0)

    if data_min < 0:
        return (None, 0.0)

    try:
        params = stats.expon.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.expon.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        loc, scale = params

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            expon=ExponentialDistribution(
                loc=round(loc, MAX_PRECISION),
                scale=round(scale, MAX_PRECISION),
            ),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_weibull_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierResult,
    precision: int | None,
) -> tuple[NumberHint | None, float]:
    """Try fitting Weibull distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Weibull distribution has shape and scale parameters requiring substantial data for reliable fitting
    if len(data) < MIN_SAMPLES_WEIBULL:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.weibull_min.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.weibull_min.cdf, args=params)

        if ks_p_value < KS_TEST_P_VALUE_THRESHOLD:
            return (None, 0.0)

        min_val = round(outliers.iqr_lower, precision)
        max_val = round(outliers.iqr_upper, precision)

        c, loc, scale = params

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            weibull=WeibullDistribution(
                c=round(c, MAX_PRECISION),
                loc=round(loc, MAX_PRECISION),
                scale=round(scale, MAX_PRECISION),
            ),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


# Distribution fitters ordered by likelihood for typical data
DISTRIBUTION_FITTERS = [
    _try_normal_distribution,
    _try_uniform_distribution,
    _try_gamma_distribution,
    _try_lognorm_distribution,
    _try_exponential_distribution,
    _try_beta_distribution,
    _try_weibull_distribution,
]


def _get_best_distribution_hint(values: Sequence[int | float], precision: int | None) -> NumberHint | None:
    """Try all distribution fitters and return the best hint."""
    # Minimal data preparation
    data = np.array(values)
    clean_data = data[np.isfinite(data)]

    outliers = _detect_outliers(clean_data)
    fit_data = outliers.data_without_extreme_outliers
    data_min = float(np.min(fit_data))

    # Try each distribution fitter
    best_score = float("inf")
    best_hint = None

    for fitter in DISTRIBUTION_FITTERS:
        hint, score = fitter(fit_data, data_min, outliers, precision)
        if hint and score < best_score:
            best_score = score
            best_hint = hint

    return best_hint
