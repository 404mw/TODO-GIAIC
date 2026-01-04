# Detailed Safety Examples

## Example 1: Blocking Unsafe Delete

### User Request
"Add a delete task endpoint: DELETE /api/tasks/:id"

### Response
```
🚫 DATA SAFETY VIOLATION

Constitution Section III: Data Integrity & Safety
Principle: "User data loss is unacceptable" (III.1)

Operation: Implement DELETE endpoint for tasks
Risk Level: HIGH (permanent data deletion)

Issues Found:

❌ No Soft Delete
   Problem: Hard delete removes data permanently
   Requirement: Implement soft delete (mark as deleted, retain in DB)

❌ No Confirmation Flow
   Problem: API endpoint doesn't require confirmation
   Requirement: Frontend must show confirmation dialog

❌ No Undo Mechanism
   Problem: Deletion cannot be undone
   Requirement: Undo must be available per Section III.4

❌ No Backup Strategy Mentioned
   Problem: No evidence of backup system
   Requirement: Automated daily backups required (Section III.2)

Required Safeguards:

1. **Implement Soft Delete**
   See: `.claude/skills/data-safety-guardian/patterns.md` (Soft Delete Pattern)

2. **Add Confirmation in Frontend**
   See: `.claude/skills/data-safety-guardian/patterns.md` (Frontend Delete with Undo)

3. **Implement Undo**
   See: `.claude/skills/data-safety-guardian/patterns.md` (Undo Implementation Pattern)

4. **Implement Backup Strategy**
   See: `.claude/skills/data-safety-guardian/patterns.md` (Backup Strategy Requirements)

Approve safe implementation with all safeguards?
```

## Example 2: Approving Safe Update

### User Request
"Add endpoint to update task title"

### Response
```
✅ DATA SAFETY CHECK PASSED

Operation: Implement PUT /api/tasks/:id for title updates
Risk Level: MEDIUM (data modification, not deletion)

Safety Verified:
✓ Undo available: Previous title can be captured and restored
✓ Dummy data: Tests will use fake tasks
✓ Backup: Automated backups protect against corruption
✓ Validation: Pydantic ensures valid input (no empty titles)

Recommended Implementation:

See: `.claude/skills/data-safety-guardian/patterns.md` (Update with Undo)

This implementation is safe. Proceed?
```

## Example 3: Blocking Real Data in Tests

### User Request
"Write tests for the task API using my existing tasks"

### Response
```
🚫 DATA SAFETY VIOLATION

Constitution Section III.3: Dummy-First Rule
Principle: "All development and testing must use dummy data by default"

Operation: Write tests using real user data
Risk Level: CRITICAL (violates data protection)

Issues Found:

❌ Using Production/Real Data
   Problem: Tests are accessing real user tasks
   Requirement: Tests MUST use dummy/fake data only

❌ Data Corruption Risk
   Problem: Tests may modify or delete real data
   Consequence: User data loss is unacceptable (III.1)

❌ Privacy Violation
   Problem: Real user data exposed in test logs
   Consequence: Sensitive data may be leaked

Required Actions:

See: `.claude/skills/data-safety-guardian/patterns.md` (Dummy Data for Testing)

Safe Testing Approach:

✓ Isolated test database (never touches production)
✓ Dummy data fixtures (obviously fake)
✓ Cleanup after tests (no data persists)
✓ No real user data accessed

Proceed with safe testing using dummy data only?
```

## Example 4: Bulk Delete Safety

### User Request
"Add feature to delete all completed tasks"

### Response
```
⚠️ HIGH-RISK BULK OPERATION DETECTED

Constitution Section III: Data Integrity & Safety
Operation: Bulk delete completed tasks
Risk Level: VERY HIGH (mass data deletion)

Required Safeguards (ALL mandatory):

1. **Preview Before Deletion**
2. **Rate Limiting**
3. **Batch Undo**
4. **Soft Delete Only**
5. **Audit Logging**

See: `.claude/skills/data-safety-guardian/patterns.md` (Bulk Operations Pattern)

Constitutional Compliance:
✓ User data loss unacceptable → Soft delete only
✓ Undo guarantee → Batch undo implemented
✓ Confirmation → Preview shown before execution
✓ Safety limits → Max 100 items per batch

Approve bulk delete with all safeguards?
```
