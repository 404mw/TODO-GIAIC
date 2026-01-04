# Safety Checklists by Operation Type

## Read-Only Operations (Low Risk)

- No safety checks required
- Proceed normally

## Update Operations (Medium Risk)

### Check 1: Undo Available
```
❓ Is undo implemented for this update?
```
- [ ] Update is logged (can be reversed)
- [ ] Previous state is captured
- [ ] Undo available in current session
- [ ] Undo is guaranteed (not best-effort)

### Check 2: Test Data Only
```
❓ Are we using dummy data for testing?
```
- [ ] Tests use dummy/fake data
- [ ] No real user data in test database
- [ ] Production data never used for development

## Delete Operations (High Risk)

### Check 1: Soft Delete Preferred
```
❓ Is this a soft delete (marking as deleted) or hard delete?
```
Prefer: Soft delete (mark as deleted, keep in DB)
Avoid: Hard delete (permanent removal)

### Check 2: Confirmation Required
```
❓ Does the user confirm deletion?
```
- [ ] User explicitly confirms
- [ ] Confirmation shows what will be deleted
- [ ] Confirmation is not just implied

### Check 3: Undo Available
```
❓ Can this deletion be undone?
```
- [ ] Soft delete allows restore
- [ ] Undo available immediately after delete
- [ ] Undo persists until next mutation

### Check 4: Backup Verified
```
❓ Is backup strategy in place?
```
- [ ] Automated backups configured
- [ ] Backup tested (restore verified)
- [ ] Backup frequency meets needs (daily minimum)

## Bulk Operations (Very High Risk)

**All delete checks PLUS:**

### Check 5: Preview Required
```
❓ Does user see what will be affected before confirming?
```
- [ ] List of items to be modified/deleted shown
- [ ] Count of affected items displayed
- [ ] User can review before proceeding

### Check 6: Rate Limiting
```
❓ Is there a limit on bulk operations?
```
- [ ] Maximum bulk size defined (e.g., 100 items)
- [ ] Prevents accidental mass deletion
- [ ] Option to batch if exceeds limit

### Check 7: Batch Undo
```
❓ Can the entire bulk operation be undone?
```
- [ ] All items in batch linked (batch ID)
- [ ] Single undo reverts entire batch
- [ ] Partial undo available if needed
