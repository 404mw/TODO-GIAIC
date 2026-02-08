"""RRULE utility functions for recurring task management.

Provides utilities for parsing, validating, and working with RFC 5545 RRULE
recurrence rules using python-dateutil.

T145: Implement rrule utility functions per research.md Section 10
T158: Add human-readable RRULE description utility
"""

from datetime import datetime, UTC
from typing import Any

from dateutil.rrule import rrule, rrulestr, DAILY, WEEKLY, MONTHLY, YEARLY


class InvalidRRuleError(Exception):
    """Raised when an RRULE string is invalid or cannot be parsed."""

    def __init__(self, rrule_string: str, message: str | None = None):
        self.rrule_string = rrule_string
        self.message = message or f"Invalid RRULE: {rrule_string}"
        super().__init__(self.message)


def parse_rrule(
    rrule_string: str,
    dtstart: datetime | None = None,
) -> rrule:
    """Parse an RRULE string into a dateutil rrule object.

    Args:
        rrule_string: RFC 5545 RRULE string (e.g., "FREQ=DAILY;INTERVAL=1")
        dtstart: Optional start datetime for the recurrence rule.
                 Defaults to current UTC time if not provided.

    Returns:
        A dateutil rrule object that can be used to calculate occurrences.

    Raises:
        InvalidRRuleError: If the RRULE string is invalid or cannot be parsed.

    Examples:
        >>> parse_rrule("FREQ=DAILY;INTERVAL=1")
        <dateutil.rrule.rrule object>

        >>> parse_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        <dateutil.rrule.rrule object>
    """
    if not rrule_string or not rrule_string.strip():
        raise InvalidRRuleError(rrule_string, "RRULE string cannot be empty")

    if dtstart is None:
        dtstart = datetime.now(UTC)

    try:
        # rrulestr can parse RRULE strings with or without the "RRULE:" prefix
        # We ensure the string is properly formatted
        rrule_str = rrule_string.strip()
        if not rrule_str.upper().startswith("RRULE:"):
            rrule_str = f"RRULE:{rrule_str}"

        return rrulestr(rrule_str, dtstart=dtstart)
    except (ValueError, KeyError) as e:
        raise InvalidRRuleError(rrule_string, str(e)) from e


def validate_rrule(rrule_string: str) -> bool:
    """Validate an RRULE string without raising exceptions.

    Args:
        rrule_string: RFC 5545 RRULE string to validate.

    Returns:
        True if the RRULE is valid, False otherwise.

    Examples:
        >>> validate_rrule("FREQ=DAILY")
        True

        >>> validate_rrule("INVALID")
        False
    """
    try:
        parse_rrule(rrule_string)
        return True
    except InvalidRRuleError:
        return False


def calculate_next_due(
    rrule_string: str,
    after: datetime,
    dtstart: datetime | None = None,
) -> datetime | None:
    """Calculate the next occurrence of a recurrence rule after a given date.

    Args:
        rrule_string: RFC 5545 RRULE string.
        after: The datetime to find the next occurrence after.
               The returned datetime will be strictly greater than this.
        dtstart: Optional start datetime for the recurrence.
                 If not provided, uses the 'after' datetime.

    Returns:
        The next occurrence datetime, or None if no more occurrences exist
        (e.g., for rules with COUNT or UNTIL that have been exhausted).

    Raises:
        InvalidRRuleError: If the RRULE string is invalid.

    Examples:
        >>> from datetime import datetime, UTC
        >>> now = datetime.now(UTC)
        >>> calculate_next_due("FREQ=DAILY;INTERVAL=1", after=now)
        datetime(...)  # Tomorrow
    """
    effective_dtstart = dtstart if dtstart is not None else after

    rule = parse_rrule(rrule_string, dtstart=effective_dtstart)

    # Use after() to get the next occurrence strictly after 'after'
    # inc=False means the 'after' date itself is excluded
    next_occurrence = rule.after(after, inc=False)

    return next_occurrence


def get_rrule_components(rrule_string: str) -> dict[str, Any]:
    """Extract components from an RRULE string.

    Args:
        rrule_string: RFC 5545 RRULE string.

    Returns:
        Dictionary with parsed components like freq, interval, byday, etc.

    Raises:
        InvalidRRuleError: If the RRULE string is invalid.
    """
    rule = parse_rrule(rrule_string)

    components = {
        "freq": rule._freq,
        "interval": rule._interval,
        "count": rule._count,
        "until": rule._until,
        "byweekday": rule._byweekday,
        "bymonth": rule._bymonth,
        "bymonthday": rule._bymonthday,
        "byyearday": rule._byyearday,
        "byweekno": rule._byweekno,
        "bysetpos": rule._bysetpos,
    }

    return components


# Frequency constants mapping
FREQ_NAMES = {
    YEARLY: "yearly",
    MONTHLY: "monthly",
    WEEKLY: "weekly",
    DAILY: "daily",
}

# Day name mappings
DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

DAY_ABBREVS = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


def _ordinal(n: int) -> str:
    """Convert integer to ordinal string (1st, 2nd, 3rd, etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{n}{suffix}"


def to_human_readable(rrule_string: str) -> str:
    """Convert an RRULE string to a human-readable description.

    Args:
        rrule_string: RFC 5545 RRULE string.

    Returns:
        A human-readable description of the recurrence pattern.
        Returns the original string or an error message if parsing fails.

    Examples:
        >>> to_human_readable("FREQ=DAILY;INTERVAL=1")
        "Every day"

        >>> to_human_readable("FREQ=WEEKLY;BYDAY=MO,WE,FR")
        "Every week on Monday, Wednesday, Friday"

        >>> to_human_readable("FREQ=MONTHLY;BYMONTHDAY=1")
        "Every month on the 1st"
    """
    try:
        components = get_rrule_components(rrule_string)
    except InvalidRRuleError:
        return rrule_string  # Return original string if parsing fails

    freq = components.get("freq")
    interval = components.get("interval", 1)
    byweekday = components.get("byweekday")
    bymonthday = components.get("bymonthday")
    count = components.get("count")
    until = components.get("until")

    parts = []

    # Build frequency part
    freq_name = FREQ_NAMES.get(freq, "")

    if interval == 1:
        if freq == DAILY:
            parts.append("Every day")
        elif freq == WEEKLY:
            parts.append("Every week")
        elif freq == MONTHLY:
            parts.append("Every month")
        elif freq == YEARLY:
            parts.append("Every year")
    else:
        if freq == DAILY:
            parts.append(f"Every {interval} days")
        elif freq == WEEKLY:
            parts.append(f"Every {interval} weeks")
        elif freq == MONTHLY:
            parts.append(f"Every {interval} months")
        elif freq == YEARLY:
            parts.append(f"Every {interval} years")

    # Add day specification for weekly recurrence
    if freq == WEEKLY and byweekday:
        day_names = []
        for wd in byweekday:
            # byweekday can be integers or weekday objects
            if hasattr(wd, "weekday"):
                day_names.append(DAY_NAMES.get(wd.weekday, str(wd)))
            else:
                day_names.append(DAY_NAMES.get(wd, str(wd)))

        if day_names:
            parts.append(f"on {', '.join(day_names)}")

    # Add day specification for monthly recurrence
    if freq == MONTHLY and bymonthday:
        if isinstance(bymonthday, (list, tuple)):
            day_ordinals = [_ordinal(d) for d in bymonthday]
            parts.append(f"on the {', '.join(day_ordinals)}")
        else:
            parts.append(f"on the {_ordinal(bymonthday)}")

    # Add count if specified
    if count:
        parts.append(f"({count} times)")

    # Add until if specified
    if until:
        parts.append(f"until {until.strftime('%Y-%m-%d')}")

    return " ".join(parts) if parts else rrule_string


def get_next_n_occurrences(
    rrule_string: str,
    n: int,
    after: datetime | None = None,
    dtstart: datetime | None = None,
) -> list[datetime]:
    """Get the next N occurrences of a recurrence rule.

    Args:
        rrule_string: RFC 5545 RRULE string.
        n: Number of occurrences to return.
        after: Starting point for occurrences (defaults to now).
        dtstart: Start datetime for the recurrence rule.

    Returns:
        List of up to N datetime objects representing the next occurrences.

    Raises:
        InvalidRRuleError: If the RRULE string is invalid.
    """
    if after is None:
        after = datetime.now(UTC)

    if dtstart is None:
        dtstart = after

    rule = parse_rrule(rrule_string, dtstart=dtstart)

    occurrences = []
    current = after

    for _ in range(n):
        next_occ = rule.after(current, inc=False)
        if next_occ is None:
            break
        occurrences.append(next_occ)
        current = next_occ

    return occurrences
