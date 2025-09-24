"""Numeric analysis for sample data including statistical distribution analysis."""

from collections import Counter
from collections.abc import KeysView
from dataclasses import dataclass

import numpy as np
from scipy import stats

from factoreally.constants import MAX_PRECISION
from factoreally.hints import ConstantValueHint, NumberHint
from factoreally.hints.base import AnalysisHint, SimpleType


@dataclass
class OutlierBounds:
    """Bounds for outlier detection."""

    iqr_lower: float
    iqr_upper: float
    extreme_lower: float
    extreme_upper: float


@dataclass
class OutlierValues:
    """Outlier values categorized by severity."""

    moderate: list[float]
    extreme: list[float]


@dataclass
class OutlierAnalysis:
    """Results from outlier analysis."""

    method: str
    total_values: int
    moderate_outliers_count: int
    extreme_outliers_count: int
    z_outliers_count: int
    moderate_outlier_rate: float
    extreme_outlier_rate: float
    data_without_extreme_outliers: np.ndarray
    outlier_values: OutlierValues
    bounds: OutlierBounds


class NumericAnalyzer:
    """Analyzes numeric data for factory generation including statistical distributions."""

    def __init__(self) -> None:
        self.field_hints: dict[str, AnalysisHint] = {}

    def analyze_all(
        self,
        field: str,
        value_counts: Counter[SimpleType],
    ) -> bool:
        """Analyze all values for a field across all items."""

        if not value_counts:
            return False

        values: list[int | float] = []

        is_integer = True
        for value, count in value_counts.items():
            if type(value) is float:
                is_integer = False
            elif type(value) is not int:
                return False
            values.extend(value for _ in range(count))

        precision = None if is_integer else _calculate_precision(value_counts.keys())

        if len(value_counts.keys()) == 1:
            self.field_hints[field] = NumberHint(
                min=values[0],
                max=values[0],
            )
        elif hint := _get_best_distribution_hint(values, precision):
            self.field_hints[field] = hint
        else:
            self.field_hints[field] = NumberHint(
                min=round(min(values), precision),
                max=round(max(values), precision),
                prec=precision,
            )

        return True

    def get_hint(self, field: str) -> AnalysisHint | None:
        return self.field_hints.get(field)


def _calculate_precision(values: KeysView[SimpleType]) -> int | None:
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


def _detect_outliers(data: np.ndarray) -> OutlierAnalysis:
    """Detect outliers using multiple methods."""
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1

    # IQR method
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    moderate_outliers = (data < lower_bound) | (data > upper_bound)

    # Extreme outliers (3 * IQR)
    extreme_lower = q1 - 3 * iqr
    extreme_upper = q3 + 3 * iqr
    extreme_outliers = (data < extreme_lower) | (data > extreme_upper)

    # Z-score method (for normally distributed data)
    z_scores = np.abs(stats.zscore(data))
    z_outliers = z_scores > 3

    return OutlierAnalysis(
        method="IQR + Z-score",
        total_values=len(data),
        moderate_outliers_count=int(np.sum(moderate_outliers)),
        extreme_outliers_count=int(np.sum(extreme_outliers)),
        z_outliers_count=int(np.sum(z_outliers)),
        moderate_outlier_rate=float(np.sum(moderate_outliers) / len(data)),
        extreme_outlier_rate=float(np.sum(extreme_outliers) / len(data)),
        data_without_extreme_outliers=data[~extreme_outliers],
        outlier_values=OutlierValues(
            moderate=data[moderate_outliers].tolist(),
            extreme=data[extreme_outliers].tolist(),
        ),
        bounds=OutlierBounds(
            iqr_lower=float(lower_bound),
            iqr_upper=float(upper_bound),
            extreme_lower=float(extreme_lower),
            extreme_upper=float(extreme_upper),
        ),
    )


def _try_normal_distribution(
    data: np.ndarray,
    data_min: float,  # noqa: ARG001
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting normal distribution."""
    # Normal distribution needs sufficient data to estimate mean and std reliably
    if len(data) < 15:
        return (None, 0.0)

    try:
        params = stats.norm.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.norm.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        mean, std = params
        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(
            min=min_val, max=max_val, prec=precision, mean=round(mean, MAX_PRECISION), std=round(std, MAX_PRECISION)
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_uniform_distribution(
    data: np.ndarray,
    data_min: float,  # noqa: ARG001
    outliers: OutlierAnalysis,  # noqa: ARG001
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting uniform distribution."""
    # Uniform distribution needs enough data to distinguish from other patterns
    if len(data) < 6:
        return (None, 0.0)

    try:
        params = stats.uniform.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.uniform.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        loc, scale = params
        min_val = round(loc, precision)
        max_val = round(loc + scale, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_gamma_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting gamma distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Gamma distribution has 3 parameters and requires substantial data for reliable fitting
    if len(data) < 20:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.gamma.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.gamma.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        alpha, loc, scale = params
        beta = 1 / scale if scale != 0 else 1
        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(
            min=min_val,
            max=max_val,
            prec=precision,
            alpha=round(alpha, MAX_PRECISION),
            beta=round(beta, MAX_PRECISION),
            loc=round(loc, MAX_PRECISION),
        )
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_beta_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting beta distribution. Returns (None, 0.0) if data not in [0,1] range."""
    # Beta distribution has 2 shape parameters requiring sufficient data for reliable estimation
    if len(data) < 12:
        return (None, 0.0)

    data_max = float(np.max(data))
    if not (data_min >= 0 and data_max <= 1):
        return (None, 0.0)

    try:
        params = stats.beta.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.beta.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        # Beta distribution uses IQR bounds from outlier analysis
        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_lognorm_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting log-normal distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Log-normal distribution needs sufficient data to verify log-normality pattern
    if len(data) < 15:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.lognorm.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.lognorm.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_exponential_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting exponential distribution. Returns (None, 0.0) if data contains negative values."""
    # Exponential distribution needs sufficient data to verify exponential decay pattern
    if len(data) < 10:
        return (None, 0.0)

    if data_min < 0:
        return (None, 0.0)

    try:
        params = stats.expon.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.expon.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
        return (hint, ks_stat)  # noqa: TRY300
    except (ValueError, RuntimeError, TypeError, AttributeError):
        return (None, 0.0)


def _try_weibull_distribution(
    data: np.ndarray,
    data_min: float,
    outliers: OutlierAnalysis,
    precision: int | None,
) -> tuple[AnalysisHint | None, float]:
    """Try fitting Weibull distribution. Returns (None, 0.0) if data contains non-positive values."""
    # Weibull distribution has shape and scale parameters requiring substantial data for reliable fitting
    if len(data) < 18:
        return (None, 0.0)

    if data_min <= 0:
        return (None, 0.0)

    try:
        params = stats.weibull_min.fit(data)
        ks_stat, ks_p_value = stats.kstest(data, stats.weibull_min.cdf, args=params)

        if ks_p_value < 0.05:
            return (None, 0.0)

        min_val = round(outliers.bounds.iqr_lower, precision)
        max_val = round(outliers.bounds.iqr_upper, precision)

        if min_val == max_val:
            return (ConstantValueHint(val=min_val), ks_stat)

        hint = NumberHint(min=min_val, max=max_val, prec=precision)
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


def _get_best_distribution_hint(values: list[int | float], precision: int | None) -> AnalysisHint | None:
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
