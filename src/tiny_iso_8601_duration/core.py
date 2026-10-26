"""Parse and format ISO 8601 durations.

The canonical ISO 8601 duration form is P[n]Y[n]M[n]DT[n]H[n]M[n]S. Python's
stdlib datetime.timedelta does not represent years or months, because those
units are calendar-relative, not fixed. We resolve that by adopting the fixed
conversions defined by ISO 8601 itself: one year = 365 days, one month = 30
days. This keeps round-tripping predictable and testable, at the cost of
matching wall-clock arithmetic for dates near month/year boundaries.
"""

from __future__ import annotations

import re
from datetime import timedelta


__all__ = ["parse_duration", "format_duration", "ISO8601DurationError"]


_DAYS_PER_YEAR = 365
_DAYS_PER_MONTH = 30
_SECONDS_PER_MINUTE = 60
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_DAY = 86400

_PATTERN = re.compile(
    r"^"
    r"P"
    r"(?!$)"
    r"(?:(?P<years>\d+(?:\.\d+)?)Y)?"
    r"(?:(?P<months>\d+(?:\.\d+)?)M)?"
    r"(?:(?P<weeks>\d+(?:\.\d+)?)W)?"
    r"(?:(?P<days>\d+(?:\.\d+)?)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+(?:\.\d+)?)H)?"
    r"(?:(?P<minutes>\d+(?:\.\d+)?)M)?"
    r"(?:(?P<seconds>\d+(?:\.\d+)?)S)?"
    r")?"
    r"$",
    re.IGNORECASE,
)


class ISO8601DurationError(ValueError):
    """Raised when a string is not a valid ISO 8601 duration."""


def _to_microseconds(value: float) -> int:
    """Return the rounded-to-microseconds integer of *value*.

    timedelta stores microseconds as an int; we round to avoid dropping the
    sub-second tail that float arithmetic produces.
    """
    return int(round(value * 1_000_000))


def parse_duration(text: str) -> timedelta:
    """Parse an ISO 8601 duration string into a timedelta.

    Years and months are converted using ISO 8601's fixed unit durations:
    1 year = 365 days, 1 month = 30 days. This avoids calendar ambiguity at the
    cost of not matching wall-clock arithmetic for dates near month/year
    boundaries. The decision is deliberate and documented in the README.
    """
    if not isinstance(text, str):
        raise ISO8601DurationError(f"expected str, got {type(text).__name__}")
    if not text:
        raise ISO8601DurationError("empty duration string")

    match = _PATTERN.match(text)
    if match is None:
        raise ISO8601DurationError(f"invalid ISO 8601 duration: {text!r}")

    groups = match.groupdict()
    if not any(groups.values()):
        raise ISO8601DurationError(f"duration has no components: {text!r}")

    total_days = 0.0
    total_seconds = 0.0

    years = groups.get("years")
    months = groups.get("months")
    weeks = groups.get("weeks")
    days = groups.get("days")
    hours = groups.get("hours")
    minutes = groups.get("minutes")
    seconds = groups.get("seconds")

    if years is not None:
        total_days += float(years) * _DAYS_PER_YEAR
    if months is not None:
        total_days += float(months) * _DAYS_PER_MONTH
    if weeks is not None:
        total_days += float(weeks) * 7
    if days is not None:
        total_days += float(days)
    if hours is not None:
        total_seconds += float(hours) * _SECONDS_PER_HOUR
    if minutes is not None:
        total_seconds += float(minutes) * _SECONDS_PER_MINUTE
    if seconds is not None:
        total_seconds += float(seconds)

    total_us = (
        _to_microseconds(total_days * _SECONDS_PER_DAY)
        + _to_microseconds(total_seconds)
    )
    try:
        return timedelta(microseconds=total_us)
    except (ValueError, OverflowError) as exc:
        raise ISO8601DurationError(f"duration out of range: {text!r}") from exc


def format_duration(td: timedelta) -> str:
    """Format a timedelta as an ISO 8601 duration string.

    The result uses only days, hours, minutes, and seconds. Years and months
    are intentionally omitted because timedelta cannot represent them, and any
    conversion back would lose information.
    """
    if not isinstance(td, timedelta):
        raise ISO8601DurationError(f"expected timedelta, got {type(td).__name__}")

    total_seconds = td.total_seconds()
    if total_seconds < 0:
        raise ISO8601DurationError("timedelta must be non-negative")

    days, rem = divmod(total_seconds, _SECONDS_PER_DAY)
    hours, rem = divmod(rem, _SECONDS_PER_HOUR)
    minutes, seconds = divmod(rem, _SECONDS_PER_MINUTE)

    parts = ["P"]
    if days:
        parts.append(f"{int(days)}D")
    time_parts = []
    if hours:
        time_parts.append(f"{int(hours)}H")
    if minutes:
        time_parts.append(f"{int(minutes)}M")
    if seconds:
        if seconds == int(seconds):
            time_parts.append(f"{int(seconds)}S")
        else:
            time_parts.append(f"{seconds:g}S")

    if time_parts:
        parts.append("T")
        parts.extend(time_parts)

    result = "".join(parts)
    if result == "P":
        return "PT0S"
    return result
