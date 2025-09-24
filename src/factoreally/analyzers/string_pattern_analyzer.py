"""String pattern analysis combining temporal and structured pattern detection."""

import re
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime

from factoreally.constants import MAX_PRECISION
from factoreally.hints import (
    Auth0IdHint,
    DateHint,
    DatetimeHint,
    DurationRangeHint,
    MacAddressHint,
    NumberStringHint,
    TextHint,
    Uuid4Hint,
    VersionHint,
)
from factoreally.hints.base import AnalysisHint, SimpleType


def create_iso_z_mixed_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for ISO Z timestamp pattern (with optional fractional seconds)."""
    # Check if all values match the flexible ISO Z pattern (with optional fractional seconds)
    if not all(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "iso_z_mixed")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_iso_mixed_tz_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for ISO timestamp pattern (Z and/or timezone offsets)."""
    # Check if all values match either Z format or timezone offset format
    if not all(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "iso_mixed_tz")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_iso_with_tz_microseconds_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for ISO with timezone microseconds timestamp pattern."""
    if not all(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2}$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "iso_with_tz_microseconds")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_unix_seconds_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for Unix seconds timestamp pattern."""
    if not all(re.match(r"^\d{10}$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "unix_seconds")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_unix_milliseconds_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for Unix milliseconds timestamp pattern."""
    if not all(re.match(r"^\d{13}$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "unix_milliseconds")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_datetime_space_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for space-separated datetime pattern."""
    if not all(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "%Y-%m-%d %H:%M:%S")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def create_datetime_us_hint(values: list[str]) -> AnalysisHint | None:
    """Create DatetimeHint for US datetime pattern."""
    if not all(re.match(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$", v) for v in values):
        return None

    timestamps = []
    for value in values:
        parsed = _parse_timestamp(value, "%m/%d/%Y %H:%M:%S")
        if parsed:
            timestamps.append(parsed)

    if timestamps:
        return DatetimeHint(
            min=min(timestamps).isoformat(),
            max=max(timestamps).isoformat(),
        )
    return None


def _validate_duration_values(values: list[str], pattern: str) -> tuple[bool, bool, bool]:
    """Validate duration values and return (all_valid, has_days, has_fractional)."""
    has_days = False
    has_fractional = False

    for value in values:
        match = re.match(pattern, value)
        if not match:
            return False, False, False

        if match.group(1):  # days component
            has_days = True
        if match.group(5):  # fractional component (with dot)
            has_fractional = True

    return True, has_days, has_fractional


def _determine_duration_format(*, has_days: bool, has_fractional: bool) -> str:
    """Determine duration format based on components present."""
    if has_days and has_fractional:
        return "D.HMS.F"
    if has_days:
        return "D.HMS"
    return "HMS"


def create_duration_hint(values: list[str]) -> AnalysisHint | None:
    """Create DurationRangeHint for duration patterns (HMS, D.HMS, or D.HMS.F)."""
    if not values:
        return None

    # Single pattern with optional day and fractional components
    pattern = r"^(\d+\.)?(\d{1,2}):(\d{2}):(\d{2})(\.(\d+))?$"

    # Validate all values and determine format
    all_valid, has_days, has_fractional = _validate_duration_values(values, pattern)
    if not all_valid:
        return None

    fmt = _determine_duration_format(has_days=has_days, has_fractional=has_fractional)

    # Parse all durations using the determined format
    durations = []
    for value in values:
        duration_seconds = _parse_duration_seconds(value, fmt)
        if duration_seconds is not None:
            durations.append(duration_seconds)

    if durations:
        return DurationRangeHint(
            min=min(durations),
            max=max(durations),
            avg=round(sum(durations) / len(durations), MAX_PRECISION),
            fmt=fmt,
        )

    return None


def create_duration_iso8601_days_hint(values: list[str]) -> AnalysisHint | None:
    """Create DurationRangeHint for ISO8601 days duration pattern."""
    if not all(re.match(r"^P\d+D$", v) for v in values):
        return None

    durations = []
    for value in values:
        duration_seconds = _parse_duration_seconds(value, "ISO8601_Days")
        if duration_seconds is not None:
            durations.append(duration_seconds)

    if durations:
        return DurationRangeHint(
            min=min(durations),
            max=max(durations),
            avg=round(sum(durations) / len(durations), MAX_PRECISION),
            fmt="ISO8601_Days",
        )
    return None


def create_duration_iso8601_weeks_hint(values: list[str]) -> AnalysisHint | None:
    """Create DurationRangeHint for ISO8601 weeks duration pattern."""
    if not all(re.match(r"^P\d+W$", v) for v in values):
        return None

    durations = []
    for value in values:
        duration_seconds = _parse_duration_seconds(value, "ISO8601_Weeks")
        if duration_seconds is not None:
            durations.append(duration_seconds)

    if durations:
        return DurationRangeHint(
            min=min(durations),
            max=max(durations),
            avg=round(sum(durations) / len(durations), MAX_PRECISION),
            fmt="ISO8601_Weeks",
        )
    return None


def create_auth0_id_hint(values: list[str]) -> AnalysisHint | None:
    """Create Auth0IdHint for Auth0 ID pattern."""
    if not all(v.startswith("auth0|") for v in values):
        return None
    return Auth0IdHint()


def create_mac_address_hint(values: list[str]) -> AnalysisHint | None:
    """Create MacAddressHint for MAC address pattern."""
    if not all(re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", v) for v in values):
        return None
    return MacAddressHint()


def create_uuid_hint(values: list[str]) -> AnalysisHint | None:
    """Create Uuid4Hint for UUID pattern."""
    if not all(re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v.lower()) for v in values):
        return None
    return Uuid4Hint()


def create_version_hint(values: list[str]) -> AnalysisHint | None:
    """Create VersionHint for version pattern."""
    if not all(re.match(r"^\d+\.\d+\.\d+(\.\d+)?$", v) for v in values):
        return None
    return VersionHint(
        pattern_type="Version",
        examples=values[:3],
    )


def create_version_short_hint(values: list[str]) -> AnalysisHint | None:
    """Create VersionHint for short version pattern."""
    if not all(re.match(r"^\d+\.\d+$", v) for v in values):
        return None
    return VersionHint(pattern_type="Version_Short")


def create_date_hint(values: list[str]) -> AnalysisHint | None:
    """Create DateHint for date pattern."""
    if not all(re.match(r"^\d{4}-\d{2}-\d{2}$", v) for v in values):
        return None
    return DateHint(min=min(values), max=max(values))


def create_numeric_string_hint(values: list[str]) -> AnalysisHint | None:
    """Create NumberStringHint for numeric string pattern."""
    if not all(v.isdigit() for v in values):
        return None

    numeric_values = [float(v) for v in values]
    return NumberStringHint(
        min=min(numeric_values),
        max=max(numeric_values),
    )


def create_text_hint(values: list[str]) -> AnalysisHint | None:
    """Create TextHint for long text pattern.

    Detection logic: ≥25% of values are 'long strings' (>30 chars with ≥5 spaces).
    """
    if not values:
        return None

    # Check if at least 25% of values are long strings with multiple spaces
    long_text_count = 0
    lengths = []

    for value in values:
        lengths.append(len(value))
        # Count spaces in the value
        space_count = value.count(" ")
        if len(value) > 30 and space_count >= 5:
            long_text_count += 1

    # Require more than 25% of values to be long text with multiple spaces
    threshold = len(values) * 0.25
    if long_text_count <= threshold:
        return None

    return TextHint(
        min=min(lengths),
        max=max(lengths),
    )


# Pattern hint creators that check patterns and return hints directly
PATTERN_HINT_CREATORS: list[Callable[[list[str]], AnalysisHint | None]] = [
    # Temporal patterns - prioritize these first
    create_iso_mixed_tz_hint,
    create_iso_z_mixed_hint,
    create_iso_with_tz_microseconds_hint,
    create_unix_seconds_hint,
    create_unix_milliseconds_hint,
    create_datetime_space_hint,
    create_datetime_us_hint,
    create_duration_hint,
    create_duration_iso8601_days_hint,
    create_duration_iso8601_weeks_hint,
    # Structured patterns
    create_auth0_id_hint,
    create_mac_address_hint,
    create_uuid_hint,
    create_version_hint,
    create_version_short_hint,
    create_date_hint,
    # Numeric strings
    create_numeric_string_hint,
    # Text patterns - lowest priority as they're most general
    create_text_hint,
]


def _parse_timestamp(value: str, format_str: str) -> datetime | None:
    """Parse timestamp string using the format string."""
    try:
        # Handle special timestamp formats
        if format_str == "unix_seconds":
            return datetime.fromtimestamp(int(value), tz=UTC)

        if format_str == "unix_milliseconds":
            return datetime.fromtimestamp(int(value) / 1000, tz=UTC)

        if format_str in ("iso_with_tz", "iso_with_tz_microseconds", "iso_z_mixed", "iso_mixed_tz"):
            # Use fromisoformat for ISO formats and mixed timestamps
            return datetime.fromisoformat(value)

        # Handle strptime formats
        if ".%f" in format_str and "." not in value:
            # Handle case where format expects microseconds but value doesn't have them
            return None

        return datetime.strptime(value, format_str).replace(tzinfo=UTC)
    except (ValueError, KeyError):
        return None


def _parse_hms_duration(value: str) -> float | None:
    """Parse HMS duration format."""
    hms_match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})$", value)
    if hms_match:
        hours, minutes, seconds = map(int, hms_match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return None


def _parse_dhms_fractional_duration(value: str) -> float | None:
    """Parse D.HMS.F duration format with fractional seconds."""
    dhms_fractional_match = re.match(r"^(\d+\.)?(\d{1,2}):(\d{2}):(\d{2})\.(\d+)$", value)
    if dhms_fractional_match:
        days_str, hours_str, minutes_str, seconds_str, fractional_str = dhms_fractional_match.groups()
        days, hours, minutes, seconds = (
            int(days_str.removesuffix(".") if days_str else 0),
            int(hours_str),
            int(minutes_str),
            int(seconds_str),
        )
        # Convert fractional part to float (e.g., "9074178" -> 0.9074178)
        fractional_seconds = float(f"0.{fractional_str}")
        return days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds + fractional_seconds
    return None


def _parse_dhms_duration(value: str) -> float | None:
    """Parse D.HMS duration format."""
    dhms_match = re.match(r"^(\d+)\.(\d{1,2}):(\d{2}):(\d{2})$", value)
    if dhms_match:
        days, hours, minutes, seconds = map(int, dhms_match.groups())
        return days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds
    return None


def _parse_iso8601_duration(value: str, unit: str) -> float | None:
    """Parse ISO8601 duration format."""
    match = re.search(r"\d+", value)
    if match:
        amount = int(match.group())
        if unit == "days":
            return amount * 24 * 3600
        if unit == "weeks":
            return amount * 7 * 24 * 3600
    return None


def _parse_duration_seconds(value: str, pattern_format: str) -> float | None:
    """Parse duration value and return seconds."""
    try:
        if pattern_format == "HMS":
            return _parse_hms_duration(value)
        if pattern_format == "D.HMS.F":
            return _parse_dhms_fractional_duration(value)
        if pattern_format == "D.HMS":
            return _parse_dhms_duration(value)
        if pattern_format == "ISO8601_Days":
            return _parse_iso8601_duration(value, "days")
        if pattern_format == "ISO8601_Weeks":
            return _parse_iso8601_duration(value, "weeks")
    except ValueError:
        pass
    return None


class StringPatternAnalyzer:
    """Analyzes string patterns for factory generation."""

    def __init__(self) -> None:
        """Initialize string pattern analyzer."""
        # Field -> hint mapping for string patterns
        self.field_hints: dict[str, AnalysisHint] = {}

    def analyze_all(self, field: str, value_counts: Counter[SimpleType]) -> bool:
        """Analyze string values for consistent patterns across ALL values in the field."""
        # Extract all unique string values for this field
        string_values = [value for value in value_counts if isinstance(value, str)]

        if not string_values or len(string_values) != len(value_counts):
            return False

        # Check each pattern hint creator until one matches
        for create_hint in PATTERN_HINT_CREATORS:
            hint = create_hint(string_values)
            if hint:
                self.field_hints[field] = hint
                return True

        return False

    def get_hint(self, field: str) -> AnalysisHint | None:
        """Get pattern hint for a field."""
        return self.field_hints.get(field)
