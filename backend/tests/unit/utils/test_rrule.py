"""Unit tests for RRULE utility functions.

RED phase tests for Phase 6: User Story 3 - Recurring Task Templates.

T140, T144: Tests for RRULE parsing and next due date calculation.
"""

from datetime import datetime, timedelta, timezone, UTC
from zoneinfo import ZoneInfo

import pytest

# =============================================================================
# Module Import (will fail initially - TDD RED phase)
# =============================================================================

from src.lib.rrule import (
    parse_rrule,
    calculate_next_due,
    validate_rrule,
    to_human_readable,
    InvalidRRuleError,
)


# =============================================================================
# RRULE Parsing Tests (T140)
# =============================================================================


class TestRRuleParsing:
    """Tests for RRULE parsing (FR-015)."""

    def test_parse_daily_rrule(self):
        """T140: Parse daily RRULE pattern.

        FREQ=DAILY;INTERVAL=1 should be parsed correctly.
        """
        rrule = "FREQ=DAILY;INTERVAL=1"
        parsed = parse_rrule(rrule)

        assert parsed is not None
        # Should have daily frequency
        assert parsed._freq == 3  # dateutil.rrule.DAILY = 3

    def test_parse_weekly_rrule_with_byday(self):
        """T140: Parse weekly RRULE pattern with BYDAY.

        FREQ=WEEKLY;BYDAY=MO,WE,FR should be parsed correctly.
        """
        rrule = "FREQ=WEEKLY;BYDAY=MO,WE,FR"
        parsed = parse_rrule(rrule)

        assert parsed is not None

    def test_parse_monthly_rrule_with_bymonthday(self):
        """T140: Parse monthly RRULE pattern with BYMONTHDAY.

        FREQ=MONTHLY;BYMONTHDAY=1 should be parsed correctly.
        """
        rrule = "FREQ=MONTHLY;BYMONTHDAY=1"
        parsed = parse_rrule(rrule)

        assert parsed is not None

    def test_parse_rrule_with_interval(self):
        """T140: Parse RRULE with custom interval.

        FREQ=WEEKLY;INTERVAL=2 (every 2 weeks) should be parsed correctly.
        """
        rrule = "FREQ=WEEKLY;INTERVAL=2"
        parsed = parse_rrule(rrule)

        assert parsed is not None
        assert parsed._interval == 2

    def test_parse_rrule_with_count(self):
        """T140: Parse RRULE with COUNT limit.

        FREQ=DAILY;COUNT=5 should generate exactly 5 occurrences.
        """
        rrule = "FREQ=DAILY;COUNT=5"
        dtstart = datetime.now(UTC)
        parsed = parse_rrule(rrule, dtstart=dtstart)

        # Generate all occurrences
        occurrences = list(parsed)
        assert len(occurrences) == 5

    def test_parse_rrule_with_until(self):
        """T140: Parse RRULE with UNTIL date.

        FREQ=DAILY;UNTIL=<date> should stop at the specified date.
        """
        now = datetime.now(UTC)
        until_date = now + timedelta(days=10)
        # Format UNTIL as YYYYMMDDTHHMMSSZ
        until_str = until_date.strftime("%Y%m%dT%H%M%SZ")

        rrule = f"FREQ=DAILY;UNTIL={until_str}"
        parsed = parse_rrule(rrule, dtstart=now)

        # Should have at most 11 occurrences (day 0 through day 10)
        occurrences = list(parsed)
        assert len(occurrences) <= 11

    def test_invalid_rrule_raises_error(self):
        """T140: Invalid RRULE should raise InvalidRRuleError."""
        with pytest.raises(InvalidRRuleError):
            parse_rrule("NOT_A_VALID_RRULE")

        with pytest.raises(InvalidRRuleError):
            parse_rrule("FREQ=INVALID")

        with pytest.raises(InvalidRRuleError):
            parse_rrule("")


# =============================================================================
# Next Due Date Calculation Tests (T144)
# =============================================================================


class TestNextDueCalculation:
    """Tests for next due date calculation (FR-016)."""

    def test_calculate_next_due_daily(self):
        """T144: Calculate next due date with daily RRULE.

        RRULE.after() should return the next occurrence after a given date.
        """
        rrule = "FREQ=DAILY;INTERVAL=1"
        now = datetime.now(UTC)

        next_due = calculate_next_due(rrule, after=now)

        assert next_due is not None
        assert next_due > now
        # Should be within 24 hours
        assert next_due <= now + timedelta(hours=25)

    def test_calculate_next_due_weekly(self):
        """T144: Calculate next due date with weekly RRULE.

        Next occurrence should be within 7 days.
        """
        rrule = "FREQ=WEEKLY;BYDAY=MO"
        now = datetime.now(UTC)

        next_due = calculate_next_due(rrule, after=now)

        assert next_due is not None
        assert next_due > now
        # Should be within a week
        assert next_due <= now + timedelta(days=8)

    def test_calculate_next_due_monthly(self):
        """T144: Calculate next due date with monthly RRULE.

        Next occurrence should be within ~32 days.
        """
        rrule = "FREQ=MONTHLY;BYMONTHDAY=1"
        now = datetime.now(UTC)

        next_due = calculate_next_due(rrule, after=now)

        assert next_due is not None
        assert next_due > now
        # Should be within about a month
        assert next_due <= now + timedelta(days=32)
        # Should be on the 1st
        assert next_due.day == 1

    def test_calculate_next_due_excludes_after_date(self):
        """T144: calculate_next_due should exclude the 'after' date itself.

        If 'after' is exactly on a recurrence date, return the next one.
        """
        # Set up a specific Monday
        monday = datetime(2026, 1, 19, 10, 0, 0, tzinfo=UTC)  # A Monday

        rrule = "FREQ=WEEKLY;BYDAY=MO"
        next_due = calculate_next_due(rrule, after=monday)

        # Should be the NEXT Monday, not the same Monday
        assert next_due > monday
        assert next_due.weekday() == 0  # Monday

    def test_calculate_next_due_returns_none_when_exhausted(self):
        """T144: calculate_next_due returns None when no more occurrences.

        For RRULE with COUNT or UNTIL, should return None when exhausted.
        """
        # RRULE with COUNT=1 starting in the past
        past = datetime.now(UTC) - timedelta(days=10)
        rrule = "FREQ=DAILY;COUNT=1"

        # Calculate from well after the only occurrence
        after = datetime.now(UTC)
        next_due = calculate_next_due(rrule, after=after, dtstart=past)

        assert next_due is None

    def test_calculate_next_due_respects_dtstart(self):
        """T144: calculate_next_due should respect dtstart parameter.

        Occurrences should align with dtstart.
        """
        # Start on a specific time
        dtstart = datetime(2026, 1, 15, 9, 0, 0, tzinfo=UTC)
        rrule = "FREQ=DAILY;INTERVAL=1"

        now = datetime(2026, 1, 20, 12, 0, 0, tzinfo=UTC)
        next_due = calculate_next_due(rrule, after=now, dtstart=dtstart)

        # Next occurrence should be at 9:00 the next day
        assert next_due is not None
        assert next_due.hour == 9
        assert next_due.minute == 0


# =============================================================================
# RRULE Validation Tests
# =============================================================================


class TestRRuleValidation:
    """Tests for RRULE validation utility."""

    def test_validate_rrule_returns_true_for_valid(self):
        """validate_rrule returns True for valid RRULE strings."""
        assert validate_rrule("FREQ=DAILY") is True
        assert validate_rrule("FREQ=WEEKLY;BYDAY=MO,TU,WE") is True
        assert validate_rrule("FREQ=MONTHLY;BYMONTHDAY=15") is True
        assert validate_rrule("FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25") is True

    def test_validate_rrule_returns_false_for_invalid(self):
        """validate_rrule returns False for invalid RRULE strings."""
        assert validate_rrule("") is False
        assert validate_rrule("INVALID") is False
        assert validate_rrule("FREQ=INVALID") is False
        assert validate_rrule("FREQ=") is False


# =============================================================================
# Human Readable Description Tests (T158)
# =============================================================================


class TestHumanReadable:
    """Tests for human-readable RRULE descriptions (T158)."""

    def test_daily_rrule_description(self):
        """T158: Daily RRULE should have human-readable description."""
        desc = to_human_readable("FREQ=DAILY;INTERVAL=1")
        assert "daily" in desc.lower() or "every day" in desc.lower()

    def test_weekly_rrule_with_days_description(self):
        """T158: Weekly RRULE with specific days should be described."""
        desc = to_human_readable("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        desc_lower = desc.lower()
        assert "monday" in desc_lower or "mon" in desc_lower or "mo" in desc_lower

    def test_monthly_rrule_description(self):
        """T158: Monthly RRULE should have human-readable description."""
        desc = to_human_readable("FREQ=MONTHLY;BYMONTHDAY=1")
        desc_lower = desc.lower()
        assert "monthly" in desc_lower or "1st" in desc_lower or "1" in desc_lower

    def test_interval_included_in_description(self):
        """T158: Interval should be included in description."""
        desc = to_human_readable("FREQ=WEEKLY;INTERVAL=2")
        desc_lower = desc.lower()
        assert "2" in desc_lower or "other" in desc_lower or "bi" in desc_lower

    def test_invalid_rrule_returns_error_message(self):
        """T158: Invalid RRULE returns error or original string."""
        desc = to_human_readable("INVALID_RRULE")
        # Should not crash, returns something
        assert desc is not None
        assert len(desc) > 0
