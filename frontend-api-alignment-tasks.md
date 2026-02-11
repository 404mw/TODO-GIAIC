# Frontend API Alignment - Multi-Phase Implementation

**Branch:** `004-frontend-api-alignment`
**Base Branch:** `002-perpetua-frontend`
**Source of Truth:** `API.md` (backend/docs)
**Strategy:** Incremental phases with builds and commits after each phase

---

## Phase 1: Foundation (Response Wrappers & Error Handling) ✅

**Goal:** Create robust API client foundation with proper wrappers and error handling

**Status:** COMPLETED - Commit `b365fdd`

### 1.1 Response Wrapper Schemas
- [X] Create `frontend/src/lib/schemas/response.schema.ts`
- [X] Add `DataResponse<T>` wrapper schema for `{"data": T}`
- [X] Add `PaginatedResponse<T>` wrapper schema for `{"data": T[], "pagination": {...}}`
- [X] Add `PaginationMetaSchema` for pagination metadata
- [X] Export TypeScript types for all wrappers

### 1.2 Error Handling Schemas
- [X] Create `frontend/src/lib/schemas/error.schema.ts`
- [X] Add `ApiErrorSchema` with `code`, `message`, `details`, `request_id`
- [X] Add `ErrorResponseSchema` wrapper for `{"error": {...}}`
- [X] Add `ValidationErrorDetailSchema` for field-level errors
- [X] Create error code enum with all codes from API.md (VALIDATION_ERROR, TOKEN_EXPIRED, etc.)
- [X] Export TypeScript types for all error schemas

### 1.3 API Client Updates
- [X] Update `frontend/src/lib/api/client.ts` - Add `Idempotency-Key` to PUT method
- [X] Update `frontend/src/lib/api/client.ts` - Add `Idempotency-Key` to DELETE method
- [X] Update `handleResponse` to properly handle new error schema format
- [X] Update `ApiError` class to include `request_id` and `details` fields
- [X] Add JSDoc comments documenting response unwrapping behavior

### 1.4 Testing & Build
- [X] Run `npm run build` in frontend directory
- [X] Verify no TypeScript errors
- [ ] Test error handling with invalid requests (manual test) - **TODO: Phase 5**
- [X] Commit Phase 1: "feat: add response wrappers and improve error handling"

---

## Phase 2: Schema Alignment (Core Entities) ✅

**Goal:** Fix all schemas to match API.md exactly

**Status:** COMPLETED - Commit `1805069`

### 2.1 Authentication Schemas
- [X] Update `frontend/src/lib/schemas/auth.schema.ts` - Fix `GoogleOAuthCallbackSchema` to use `id_token` instead of `code`
- [X] Update `frontend/src/lib/schemas/auth.schema.ts` - Create `GoogleAuthResponseSchema` with `access_token`, `refresh_token`, `token_type`, `expires_in`, `user`
- [X] Update `frontend/src/lib/schemas/auth.schema.ts` - Create `RefreshTokenRequestSchema` with `refresh_token`
- [X] Update `frontend/src/lib/schemas/auth.schema.ts` - Create `RefreshTokenResponseSchema` with `access_token`, `refresh_token`, `token_type`, `expires_in`
- [X] Update `frontend/src/lib/schemas/auth.schema.ts` - Create `LogoutRequestSchema` with `refresh_token`
- [X] Remove `LoginRequestSchema` and `RegisterRequestSchema` (not in API.md)
  - **Note:** Also removed broken imports from AuthContext.tsx (minimal cleanup, full migration in Phase 4)

### 2.2 User Schemas
- [X] Update `frontend/src/lib/schemas/user.schema.ts` - Wrap responses with `DataResponse<User>`
- [X] Add JSDoc comments referencing API.md endpoints (GET /api/v1/users/me)

### 2.3 Task Schemas
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Rename `message` field to `description` throughout
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Update field constraints (`title` 1-500 chars, `description` max 5000 chars)
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Add `subtask_count` and `subtask_completed_count` to `TaskSchema`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Create `TaskDetailSchema` extending `TaskSchema` with `subtasks[]` and `reminders[]`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Create `TaskListResponseSchema` using `PaginatedResponse<Task>`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Create `TaskDetailResponseSchema` using `DataResponse<TaskDetail>`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Create `TaskForceCompleteResponseSchema` with `task`, `unlocked_achievements[]`, `streak`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Create `TaskDeleteResponseSchema` with `tombstone_id`, `recoverable_until`
- [X] Update `frontend/src/lib/schemas/task.schema.ts` - Add `version` field requirement to `UpdateTaskRequestSchema`

### 2.4 AI Schemas
- [X] Create `frontend/src/lib/schemas/ai.schema.ts`
- [X] Add `AIChatRequestSchema` with `message`, `context` (include_tasks, task_limit)
- [X] Add `AISuggestedActionSchema` with `type`, `task_id`, `description`, `data`
- [X] Add `AIChatResponseSchema` with `response`, `suggested_actions[]`, `credits_used`, `credits_remaining`, `ai_request_warning`
- [X] Add `AIGenerateSubtasksRequestSchema` with `task_id`
- [X] Add `AIGenerateSubtasksResponseSchema` with `suggested_subtasks[]`, `credits_used`, `credits_remaining`
- [X] Add `AITranscribeRequestSchema` with `audio_url`, `duration_seconds`
- [X] Add `AITranscribeResponseSchema` with `transcription`, `language`, `confidence`, `credits_used`, `credits_remaining`
- [X] Add `AIConfirmActionRequestSchema` with `action_type`, `action_data`
- [X] Add `AIConfirmActionResponseSchema` (generic data wrapper)
- [X] Add `AICreditsBalanceSchema` with nested balance object and `daily_reset_at`, `tier`
- [X] Wrap all AI responses with `DataResponse<T>`
  - **Note:** Fixed z.record() to use 2 arguments: `z.record(z.string(), z.unknown())`

### 2.5 Credit Schemas
- [X] Update `frontend/src/lib/schemas/credit.schema.ts` - Create `CreditTransactionSchema` matching API.md structure
- [X] Update `frontend/src/lib/schemas/credit.schema.ts` - Create `CreditHistoryResponseSchema` using `PaginatedResponse<CreditTransaction>`
- [X] Update `frontend/src/lib/schemas/credit.schema.ts` - Ensure `CreditBalanceSchema` matches API (daily, subscription, purchased, kickstart, total)
- [X] Update `frontend/src/lib/schemas/credit.schema.ts` - Wrap balance response with `DataResponse<CreditBalance>`

### 2.6 Testing & Build
- [X] Find all files using `message` field and update to `description` (grep search)
  - **Completed:** TaskCard.tsx, TaskDetailView.tsx, TaskForm.tsx, NewTaskModal.tsx, ConvertNoteDrawer.tsx, focus/page.tsx, tasks.fixture.ts
  - **Also updated:** Components to pass `version` field (necessary for UpdateTaskRequestSchema to work)
- [X] Run `npm run build` in frontend directory
- [X] Verify no TypeScript errors
- [X] Commit Phase 2: "feat: align all schemas with API.md contracts"

---

## Phase 3: Service Layer (API Abstraction) ✅

**Goal:** Create clean service layer abstracting all API calls

**Status:** COMPLETED - Commit `02402e4`

### 3.1 Auth Service
- [X] Create `frontend/src/lib/services/auth.service.ts`
- [X] Add `googleCallback(idToken: string)` - POST /api/v1/auth/google/callback
- [X] Add `refreshTokens(refreshToken: string)` - POST /api/v1/auth/refresh
- [X] Add `logout(refreshToken: string)` - POST /api/v1/auth/logout
- [X] Add proper error handling for all methods
- [X] Add JSDoc comments for all methods

### 3.2 Users Service
- [X] Create `frontend/src/lib/services/users.service.ts`
- [X] Add `getCurrentUser()` - GET /api/v1/users/me
- [X] Add `updateCurrentUser(data: UpdateUserRequest)` - PATCH /api/v1/users/me
- [X] Add proper response unwrapping from `DataResponse<User>`

### 3.3 Tasks Service
- [X] Create `frontend/src/lib/services/tasks.service.ts`
- [X] Add `listTasks(filters?)` - GET /api/v1/tasks with query params
- [X] Add `getTask(taskId: string)` - GET /api/v1/tasks/{task_id}
- [X] Add `createTask(data: CreateTaskRequest)` - POST /api/v1/tasks
- [X] Add `updateTask(taskId: string, data: UpdateTaskRequest & {version})` - PATCH /api/v1/tasks/{task_id}
- [X] Add `forceCompleteTask(taskId: string, version: number)` - POST /api/v1/tasks/{task_id}/force-complete
- [X] Add `deleteTask(taskId: string)` - DELETE /api/v1/tasks/{task_id}
- [X] Add proper response unwrapping for all methods
- [X] Add JSDoc comments with API.md references

### 3.4 Subtasks Service
- [X] Create `frontend/src/lib/services/subtasks.service.ts`
- [X] Add `createSubtask(taskId: string, data: CreateSubtaskRequest)` - POST /api/v1/tasks/{task_id}/subtasks
- [X] Add `updateSubtask(subtaskId: string, data: UpdateSubtaskRequest)` - PATCH /api/v1/subtasks/{subtask_id}
- [X] Add `deleteSubtask(subtaskId: string)` - DELETE /api/v1/subtasks/{subtask_id}
- [X] Add proper response unwrapping

### 3.5 AI Service
- [X] Create `frontend/src/lib/services/ai.service.ts`
- [X] Add `chat(message: string, context?)` - POST /api/v1/ai/chat with required Idempotency-Key
- [X] Add `chatStream(message: string, context?)` - POST /api/v1/ai/chat/stream (SSE)
  - **Note:** SSE streaming placeholder added (requires EventSource implementation)
- [X] Add `generateSubtasks(taskId: string)` - POST /api/v1/ai/generate-subtasks with required Idempotency-Key
- [X] Add `transcribeVoice(audioUrl: string, durationSeconds: number)` - POST /api/v1/ai/transcribe (Pro only)
- [X] Add `confirmAction(actionType: string, actionData: any)` - POST /api/v1/ai/confirm-action
- [X] Add `getCredits()` - GET /api/v1/ai/credits
- [X] Add proper error handling for credit errors (INSUFFICIENT_CREDITS, TIER_REQUIRED)
- [X] Add JSDoc comments documenting credit costs and tier requirements

### 3.6 Credits Service
- [X] Create `frontend/src/lib/services/credits.service.ts`
- [X] Add `getBalance()` - GET /api/v1/credits/balance
- [X] Add `getHistory(offset?, limit?)` - GET /api/v1/credits/history
- [X] Add proper pagination handling

### 3.7 Reminders Service
- [X] Create `frontend/src/lib/services/reminders.service.ts`
- [X] Add `createReminder(taskId: string, data: CreateReminderRequest)` - POST /api/v1/tasks/{task_id}/reminders
- [X] Add `deleteReminder(reminderId: string)` - DELETE /api/v1/reminders/{reminder_id}

### 3.8 Testing & Build
- [X] Run `npm run build` in frontend directory
- [X] Verify no TypeScript errors
- [X] Verify all service methods properly typed
- [X] Commit Phase 3: "feat: create comprehensive service layer for all API endpoints"

---

## Phase 4: Component Migration (UI Updates) ✅

**Goal:** Update all components to use new schemas and service layer

**Status:** COMPLETED - Commit `8f00421`

### 4.1 Auth Components
- [X] Update `frontend/src/lib/contexts/AuthContext.tsx` - Use new auth service and schemas
  - **Completed:** Fully integrated with authService and usersService
  - **Completed:** Implemented refresh token storage and rotation
  - **Completed:** Automatic token refresh on TOKEN_EXPIRED errors
  - **Completed:** Proper logout with refresh token revocation
- [X] Remove local `UserResponseSchema` definition (use shared schema)
- [~] Update `frontend/src/app/auth/callback/page.tsx` - Use `googleCallback` with id_token
  - **Note:** OAuth callback still uses legacy authorization code flow
  - **TODO Phase 5:** Migrate to Google Sign-In SDK + ID token flow for proper API.md compliance

### 4.2 Task Components
- [X] Find all components using task `message` field - update to `description`
  - **Completed in Phase 2:** TaskCard, TaskDetailView, TaskForm, NewTaskModal, ConvertNoteDrawer, focus/page
- [ ] Update task creation forms to use `CreateTaskRequest` schema
  - **Partial:** Forms already use correct schema fields, but not explicitly typed yet
- [X] Update task edit forms to include `version` field for optimistic locking
  - **Completed in Phase 2:** TaskForm and NewTaskModal pass version field (build fix)
- [ ] Update task list displays to show `subtask_count` / `subtask_completed_count`
- [ ] Update task detail pages to display nested `subtasks` and `reminders`
- [ ] Handle force-complete response with achievements display
- [ ] Handle task deletion with tombstone recovery option

### 4.3 AI Components
- [X] Update `frontend/src/components/tasks/AISubtasksGenerator.tsx` - Use `ai.service.generateSubtasks()`
- [X] Handle credit responses properly (display credits used and remaining)
- [X] Display credit cost indicator (1 credit badge)
- [X] Handle INSUFFICIENT_CREDITS error with upgrade prompt
- [X] Handle TIER_REQUIRED error (Pro subscription required)
- [X] Handle AI_SERVICE_UNAVAILABLE, RATE_LIMIT_EXCEEDED, TASK_NOT_FOUND errors
- [X] Add color-coded error messages (error/warning/info states)
- [X] Auto-dismiss errors after 5 seconds
- [X] Set 'source: ai' field for generated subtasks
- [ ] Create or update AI chat component to use `ai.service.chat()` - **TODO: Phase 5**
- [ ] Create or update voice transcription component (Pro-only feature) - **TODO: Phase 5**

### 4.4 Credit Components
- [ ] Update credit balance displays to use new `CreditBalance` schema
- [ ] Create or update credit history component with pagination
- [ ] Add credit cost indicators for AI features (1 credit for chat, 5/min for voice)

### 4.5 Error Handling
- [ ] Create global error handler component using new `ApiError` class
- [ ] Add user-friendly error messages for all error codes from API.md
- [ ] Handle TOKEN_EXPIRED with automatic token refresh
- [ ] Handle INSUFFICIENT_CREDITS with upgrade modal
- [ ] Handle TIER_REQUIRED with Pro upgrade prompt
- [ ] Handle RATE_LIMIT_EXCEEDED with retry-after display
- [ ] Handle version CONFLICT errors with refetch prompt

### 4.6 Testing & Build
- [X] Run `npm run build` in frontend directory
- [X] Verify no TypeScript errors (0 errors, build passed)
- [ ] Manual test: Login with Google - **TODO: Phase 5**
- [ ] Manual test: Create/update/delete tasks - **TODO: Phase 5**
- [ ] Manual test: Generate AI subtasks - **TODO: Phase 5**
- [ ] Manual test: Error handling flows - **TODO: Phase 5**
- [X] Commit Phase 4: "feat: migrate components to use new service layer (Phase 4)"

---

## Phase 5: Testing & Polish

**Goal:** Ensure production-ready frontend with comprehensive validation

### 5.1 Request/Response Validation
- [ ] Test all API calls return expected schema format
- [ ] Test pagination works correctly with offset/limit
- [ ] Test response unwrapping in all services
- [ ] Test error responses are properly parsed

### 5.2 Error Handling Flows
- [ ] Test 401 TOKEN_EXPIRED triggers token refresh
- [ ] Test 402 INSUFFICIENT_CREDITS shows credit modal
- [ ] Test 403 TIER_REQUIRED shows upgrade prompt
- [ ] Test 409 CONFLICT shows refetch option
- [ ] Test 429 RATE_LIMIT_EXCEEDED shows retry timer
- [ ] Test 503 AI_SERVICE_UNAVAILABLE shows appropriate message

### 5.3 Idempotency Behavior
- [ ] Test POST requests include Idempotency-Key header
- [ ] Test PATCH requests include Idempotency-Key header
- [ ] Test PUT requests include Idempotency-Key header
- [ ] Test DELETE requests include Idempotency-Key header
- [ ] Test duplicate requests return cached response

### 5.4 Token Refresh Flow
- [ ] Test token refresh happens automatically before expiry
- [ ] Test refresh_token is properly rotated (single-use)
- [ ] Test failed refresh redirects to login
- [ ] Test refresh_token stored securely

### 5.5 Optimistic Locking
- [ ] Test task updates include version field
- [ ] Test version conflicts are detected and handled
- [ ] Test user is prompted to refetch on conflict

### 5.6 Final Build & Commit
- [ ] Run `npm run build` in frontend directory
- [ ] Verify no TypeScript errors
- [ ] Verify no console warnings
- [ ] Run full manual test suite (auth, tasks, AI, credits)
- [ ] Commit Phase 5: "test: comprehensive validation and error handling tests"

---

## Final Checklist

- [ ] All phases completed and committed
- [ ] `npm run build` passes successfully
- [ ] All manual tests pass
- [ ] No TypeScript errors
- [ ] No breaking changes to existing functionality
- [ ] Ready to create PR to merge into `002-perpetua-frontend`

---

## Notes

- Each phase must pass `npm run build` before committing
- Commit message format: `<type>: <description>` (feat, fix, refactor, test)
- All breaking changes (like `message` → `description`) documented in commit messages
- API.md is the single source of truth - if frontend conflicts, frontend is wrong
- Test manually after each phase to catch issues early

---

**Total Tasks:** 115
**Estimated Time:** 6-8 hours (assuming no major blockers)
**Risk Level:** Medium (breaking changes to existing schemas)
**Rollback Strategy:** Revert branch if build fails or critical bugs found
