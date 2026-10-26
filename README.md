# tiny_iso_8601_duration

Parses and formats ISO 8601 duration strings (`P1Y2M3DT4H5M6S`) into Python `timedelta` objects. Zero dependencies, standard library only.

```python
from datetime import timedelta
from tiny_iso_8601_duration import parse_duration, format_duration, ISO8601DurationError

td = parse_duration("P1Y2M3DT4H5M6S")
print(td)  # 428 days, 4:05:06

formatted = format_duration(timedelta(days=3, hours=4, minutes=5, seconds=6))
print(formatted)  # P3DT4H5M6S
```

## Why this exists

`datetime.timedelta` is the natural target for ISO 8601 durations, but it has no notion of years or months — those units are calendar-relative, not fixed. This library resolves the ambiguity by adopting the fixed conversions ISO 8601 permits: one year = 365 days, one month = 30 days. The trade-off is predictability: `P1M` is always 30 days, which is easy to test and reason about, but it will not match wall-clock arithmetic for dates near month or year boundaries. If you need calendar-accurate month/year math, pair this library with a date library.

`format_duration` emits only days, hours, minutes, and seconds — it will not produce years or months, because `timedelta` cannot represent them and any conversion would be lossy.

## Edge cases

- Lowercase `t` (as in `P1dt2h`) is accepted on parse.
- Empty strings, bare `P`, and non-string inputs raise `ISO8601DurationError`.
- Negative timedeltas raise on format, since ISO 8601 durations are non-negative.
- Fractional seconds, minutes, hours, and days are supported on parse and formatted without trailing zeros on output.
