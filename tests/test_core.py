import unittest
from datetime import timedelta

from tiny_iso_8601_duration import parse_duration, format_duration, ISO8601DurationError


class ParseDurationTests(unittest.TestCase):
    def test_full_form(self):
        td = parse_duration("P1Y2M3DT4H5M6S")
        # 1y=365d, 2m=60d, 3d => 428 days; plus 4h5m6s.
        expected = timedelta(days=428, hours=4, minutes=5, seconds=6)
        self.assertEqual(td, expected)

    def test_zero_seconds(self):
        self.assertEqual(parse_duration("PT0S"), timedelta(0))

    def test_weeks(self):
        self.assertEqual(parse_duration("P1W"), timedelta(weeks=1))

    def test_date_only(self):
        self.assertEqual(parse_duration("P3D"), timedelta(days=3))

    def test_time_only(self):
        self.assertEqual(parse_duration("PT4H5M6S"), timedelta(hours=4, minutes=5, seconds=6))

    def test_hours_only(self):
        self.assertEqual(parse_duration("PT4H"), timedelta(hours=4))

    def test_minutes_only(self):
        self.assertEqual(parse_duration("PT5M"), timedelta(minutes=5))

    def test_seconds_only_integer(self):
        self.assertEqual(parse_duration("PT6S"), timedelta(seconds=6))

    def test_fractional_seconds(self):
        td = parse_duration("PT0.5S")
        self.assertEqual(td, timedelta(milliseconds=500))

    def test_fractional_hours(self):
        td = parse_duration("PT1.5H")
        self.assertEqual(td, timedelta(hours=1, minutes=30))

    def test_fractional_minutes(self):
        td = parse_duration("PT1.5M")
        self.assertEqual(td, timedelta(seconds=90))

    def test_fractional_days(self):
        td = parse_duration("P1.5D")
        self.assertEqual(td, timedelta(days=1, hours=12))

    def test_fractional_years(self):
        td = parse_duration("P0.5Y")
        self.assertEqual(td, timedelta(days=182, hours=12))

    def test_lowercase_t(self):
        td = parse_duration("P1Dt2H")
        self.assertEqual(td, timedelta(days=1, hours=2))

    def test_invalid_missing_p(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("1Y2M3D")

    def test_invalid_bare_p(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("P")

    def test_invalid_empty(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("")

    def test_invalid_non_string(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration(12345)

    def test_invalid_garbage(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("garbage")

    def test_invalid_unknown_suffix(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("P1X")

    def test_invalid_time_before_date(self):
        with self.assertRaises(ISO8601DurationError):
            parse_duration("PT1HY1")

    def test_year_month_conversion(self):
        td = parse_duration("P1Y")
        self.assertEqual(td, timedelta(days=365))
        td = parse_duration("P1M")
        self.assertEqual(td, timedelta(days=30))

    def test_combined_fractional(self):
        # PT0.1S should be 100000 microseconds.
        td = parse_duration("PT0.1S")
        self.assertEqual(td, timedelta(microseconds=100000))

    def test_large_duration(self):
        td = parse_duration("P100D")
        self.assertEqual(td, timedelta(days=100))


class FormatDurationTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_duration(timedelta(0)), "PT0S")

    def test_seconds(self):
        self.assertEqual(format_duration(timedelta(seconds=6)), "PT6S")

    def test_minutes_seconds(self):
        self.assertEqual(format_duration(timedelta(minutes=5, seconds=6)), "PT5M6S")

    def test_full_time(self):
        self.assertEqual(format_duration(timedelta(hours=4, minutes=5, seconds=6)), "PT4H5M6S")

    def test_days_and_time(self):
        self.assertEqual(format_duration(timedelta(days=3, hours=4, minutes=5, seconds=6)), "P3DT4H5M6S")

    def test_days_only(self):
        self.assertEqual(format_duration(timedelta(days=3)), "P3D")

    def test_hours_only(self):
        self.assertEqual(format_duration(timedelta(hours=4)), "PT4H")

    def test_minutes_only(self):
        self.assertEqual(format_duration(timedelta(minutes=5)), "PT5M")

    def test_fractional_seconds(self):
        td = timedelta(seconds=1.5)
        self.assertEqual(format_duration(td), "PT1.5S")

    def test_fractional_seconds_short(self):
        td = timedelta(milliseconds=100)
        self.assertEqual(format_duration(td), "PT0.1S")

    def test_negative_raises(self):
        with self.assertRaises(ISO8601DurationError):
            format_duration(timedelta(seconds=-1))

    def test_non_timedelta_raises(self):
        with self.assertRaises(ISO8601DurationError):
            format_duration(12345)


class RoundTripTests(unittest.TestCase):
    def test_round_trip_simple(self):
        original = timedelta(days=3, hours=4, minutes=5, seconds=6)
        formatted = format_duration(original)
        self.assertEqual(parse_duration(formatted), original)

    def test_round_trip_zero(self):
        original = timedelta(0)
        formatted = format_duration(original)
        self.assertEqual(parse_duration(formatted), original)

    def test_round_trip_fractional_seconds(self):
        original = timedelta(seconds=1.5)
        formatted = format_duration(original)
        self.assertEqual(parse_duration(formatted), original)


if __name__ == "__main__":
    unittest.main()
