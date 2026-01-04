---
name: data-safety-guardian
description: Prevents data loss and enforces backup/undo requirements. Use when deleting, updating, or migrating data. Ensures user data is protected and recoverable per constitution.
allowed-tools: Read, Grep, Glob
---

# Data Safety Guardian

## Purpose

Enforce Constitution Section III (Data Integrity & Safety) to prevent data loss and ensure user data protection.

## Constitutional Requirements

1. **User data loss is unacceptable** (III.1)
2. **Automated daily backups mandatory** (III.2)
3. **Dummy data for testing** (III.3)
4. **Undo guarantee for mutations** (III.4)

## Instructions

### On Data Operations

When user requests operations that affect data:

1. **Classify operation risk**
   - Read-only: Low risk
   - Update: Medium risk
   - Delete: High risk
   - Bulk operations: Very high risk

2. **Run safety checks**
   - Read detailed checklists: `.claude/skills/data-safety-guardian/checklist.md`
   - Apply checks based on operation type

3. **Block or require safeguards**
   - Do not allow unsafe operations
   - Require all safeguards before proceeding

### Safety Check Overview

- **Read-Only**: No checks required
- **Update**: Undo + test data verification
- **Delete**: Soft delete + confirmation + undo + backup
- **Bulk**: All delete checks + preview + rate limiting + batch undo

**For detailed checklists**, read: `.claude/skills/data-safety-guardian/checklist.md`

## Response Format

### When Operation is Safe

```
✅ DATA SAFETY CHECK PASSED

Operation: [description]
Risk Level: [Low/Medium/High/Very High]

Safety Verified:
✓ Undo available: [description]
✓ Dummy data: Tests use fake data only
✓ Backup: [backup strategy confirmed]
✓ Confirmation: [how user confirms]

Proceeding with safe implementation...
```

### When Operation is Unsafe

```
🚫 DATA SAFETY VIOLATION

Constitution Section III: Data Integrity & Safety
Principle: "User data loss is unacceptable" (III.1)

Operation: [description]
Risk Level: [High/Very High]

Issues Found:

❌ [Issue 1]
   Problem: [What's unsafe]
   Requirement: [What's needed]

❌ [Issue 2]
   Problem: [What's unsafe]
   Requirement: [What's needed]

Required Safeguards:

1. [Specific safeguard 1]
2. [Specific safeguard 2]

Blocking implementation until data safety is ensured.

Recommended Approach:
[Present safe alternative - refer to patterns.md for code examples]
```

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Safety Checklists**: `.claude/skills/data-safety-guardian/checklist.md`
  - Detailed checks for update/delete/bulk operations
  - Step-by-step verification requirements

- **Implementation Patterns**: `.claude/skills/data-safety-guardian/patterns.md`
  - Soft delete implementation
  - Undo mechanism code
  - Backup strategy configuration

- **Detailed Examples**: `.claude/skills/data-safety-guardian/examples.md`
  - Blocking unsafe delete
  - Approving safe update
  - Blocking real data in tests
  - Bulk delete safety

## Quick Reference

**Supreme Rule**: User data loss is unacceptable (III.1)

**Always Prefer**:
- Soft delete > Hard delete
- Confirmation > Assumption
- Undo > Permanent
- Dummy data > Real data

**Never Allow**:
- Hard delete without soft delete option
- Bulk operations without preview
- Tests using production data
- Operations without undo guarantee

## Notes

- **Read sub-modules on-demand** to avoid context bloat
- Undo is **guaranteed**, not best-effort
- Backups are mandatory in production
- All destructive operations require confirmation
