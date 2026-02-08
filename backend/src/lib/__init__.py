"""Shared library utilities for Perpetua Flow Backend."""

from src.lib.limits import (
    EffectiveLimits,
    FREE_TIER_DESCRIPTION_LIMIT,
    FREE_TIER_NOTE_LIMIT,
    FREE_TIER_SUBTASK_LIMIT,
    FREE_TIER_TASK_LIMIT,
    PRO_TIER_DESCRIPTION_LIMIT,
    PRO_TIER_NOTE_LIMIT,
    PRO_TIER_SUBTASK_LIMIT,
    PRO_TIER_TASK_LIMIT,
    get_base_subtask_limit,
    get_description_limit,
    get_effective_daily_credits,
    get_effective_note_limit,
    get_effective_subtask_limit,
    get_effective_task_limit,
)
from src.lib.rrule import (
    InvalidRRuleError,
    calculate_next_due,
    get_next_n_occurrences,
    get_rrule_components,
    parse_rrule,
    to_human_readable,
    validate_rrule,
)

__all__ = [
    # Limits
    "EffectiveLimits",
    "FREE_TIER_DESCRIPTION_LIMIT",
    "FREE_TIER_NOTE_LIMIT",
    "FREE_TIER_SUBTASK_LIMIT",
    "FREE_TIER_TASK_LIMIT",
    "PRO_TIER_DESCRIPTION_LIMIT",
    "PRO_TIER_NOTE_LIMIT",
    "PRO_TIER_SUBTASK_LIMIT",
    "PRO_TIER_TASK_LIMIT",
    "get_base_subtask_limit",
    "get_description_limit",
    "get_effective_daily_credits",
    "get_effective_note_limit",
    "get_effective_subtask_limit",
    "get_effective_task_limit",
    # RRULE utilities
    "InvalidRRuleError",
    "calculate_next_due",
    "get_next_n_occurrences",
    "get_rrule_components",
    "parse_rrule",
    "to_human_readable",
    "validate_rrule",
]
