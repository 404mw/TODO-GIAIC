# Frontend Library Directory Recovery Guide

**Date**: 2026-02-08
**Issue**: Frontend build fails with 87+ module resolution errors
**Root Cause**: `frontend/src/lib/` directory was in `.gitignore` and lost during branch reorganization

---

## Problem Summary

### What Happened
1. The `frontend/src/lib/` directory was listed in root `.gitignore` (line 13: `lib/`)
2. This was intended to ignore Python lib directories, but also ignored the frontend lib
3. During branch reorganization (removing backend from 002, creating 003), the untracked lib directory was lost
4. Frontend components have 87+ imports referencing missing files in `@/lib/*`

### Current State
- ❌ Frontend build fails: `npm run build` throws "Module not found" errors
- ❌ Cannot deploy to Vercel without the lib directory
- ✅ Backend is complete and tested (1044 tests passing)
- ✅ Architecture documentation exists describing lib structure

---

## What Was Lost

### Directory Structure (from `frontend/docs/ARCHITECTURE.md`)

```
frontend/src/lib/
├── api/
│   └── client.ts              # API client with base URL, interceptors, error handling
├── config/
│   └── limits.ts              # Feature limits (max tasks, notes, etc.)
├── contexts/
│   └── AuthContext.tsx        # Authentication context provider
├── hooks/
│   ├── useAuth.ts            # Authentication hook
│   ├── useToast.ts           # Toast notification hook
│   ├── useLocalStorage.ts    # Persistent storage hook
│   ├── useTasks.ts           # React Query hook for tasks
│   ├── useSubtasks.ts        # React Query hook for subtasks
│   ├── useNotes.ts           # React Query hook for notes
│   ├── useReminders.ts       # React Query hook for reminders
│   ├── useAchievements.ts    # React Query hook for achievements
│   └── useFocus.ts           # React Query hook for focus sessions
├── schemas/
│   ├── task.schema.ts        # Zod schema for Task (mirrors backend)
│   ├── subtask.schema.ts     # Zod schema for SubTask
│   ├── note.schema.ts        # Zod schema for Note
│   ├── reminder.schema.ts    # Zod schema for Reminder
│   ├── achievement.schema.ts # Zod schema for Achievement
│   ├── user.schema.ts        # Zod schema for User
│   ├── auth.schema.ts        # Zod schemas for login/register
│   └── common.schema.ts      # Shared types (Priority, Status, etc.)
├── stores/
│   ├── sidebar.store.ts      # Sidebar collapsed state (persisted)
│   ├── focus-mode.store.ts   # Focus mode active state
│   ├── modal.store.ts        # Modal visibility states
│   ├── command-palette.store.ts # Command palette state
│   ├── notification.store.ts # Notifications list
│   └── pending-completions.store.ts # Tasks pending completion
└── utils/
    ├── date.ts               # Date formatting utilities
    ├── recurrence.ts         # Recurrence rule parsing (rrule)
    ├── cn.ts                 # Tailwind class merger
    └── validation.ts         # Form validation helpers
```

### Estimated File Count
- **~40-45 files** need to be recreated
- Most can be generated from backend Pydantic schemas
- Stores and utilities need manual implementation based on ARCHITECTURE.md

---

## How to Recover

### Prerequisites
1. ✅ Backend deployed to Railway (get API URL)
2. ✅ Backend API documentation available
3. ✅ Backend Pydantic schemas accessible in `backend/src/models/`

### Step 1: Update `.gitignore`

**Current Issue**: Root `.gitignore` line 13 has `lib/` which catches frontend lib

**Fix Options**:

**Option A - Exclude frontend lib from ignore:**
```gitignore
# Python lib directories (but not frontend/src/lib)
lib/
lib64/
!frontend/src/lib/
```

**Option B - Be more specific:**
```gitignore
# Python lib directories
/lib/
/lib64/
backend/lib/
backend/lib64/
```

**Recommendation**: Use Option B for clarity

### Step 2: Generate Zod Schemas from Backend

The backend has complete Pydantic schemas in:
- `backend/src/models/task.py`
- `backend/src/models/subtask.py`
- `backend/src/models/note.py`
- `backend/src/models/reminder.py`
- `backend/src/models/achievement.py`
- `backend/src/models/user.py`

**Use the `schema-sync-validator` or `multi-stack-code-generator` skills**:

```bash
# This skill generates type-safe Zod schemas from Pydantic models
# Ensures frontend/backend schema alignment
```

**Manual Alternative**:
Reference backend schemas and create matching Zod schemas:

Example mapping:
```python
# Backend: backend/src/models/task.py
class Task(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(max_length=200)
    priority: Priority = Field(default=Priority.MEDIUM)
    completed: bool = Field(default=False)
```

```typescript
// Frontend: frontend/src/lib/schemas/task.schema.ts
import { z } from 'zod';

export const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().max(200),
  priority: z.enum(['low', 'medium', 'high']),
  completed: z.boolean().default(false),
  // ... rest of fields
});

export type Task = z.infer<typeof TaskSchema>;
```

### Step 3: Create API Client

**File**: `frontend/src/lib/api/client.ts`

```typescript
import { z } from 'zod';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = {
  async get<T>(endpoint: string, schema?: z.ZodType<T>): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(response.status, error.code, error.message);
    }

    const data = await response.json();
    return schema ? schema.parse(data) : data;
  },

  // Similar for post, put, delete...
};

function getToken(): string | null {
  // Get JWT from localStorage or cookie
  return localStorage.getItem('auth_token');
}
```

### Step 4: Create React Query Hooks

**File**: `frontend/src/lib/hooks/useTasks.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { TaskSchema, type Task } from '@/lib/schemas/task.schema';
import { z } from 'zod';

const TaskListSchema = z.object({
  data: z.array(TaskSchema),
});

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient.get('/tasks', TaskListSchema),
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: Partial<Task>) =>
      apiClient.post('/tasks', task, TaskSchema),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

// Similar for useUpdateTask, useDeleteTask, etc.
```

### Step 5: Create Zustand Stores

**File**: `frontend/src/lib/stores/sidebar.store.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isCollapsed: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      isCollapsed: false,
      toggle: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
    }),
    { name: 'sidebar-storage' }
  )
);
```

### Step 6: Create Utilities

**File**: `frontend/src/lib/utils/date.ts`

```typescript
import { format, formatDistanceToNow } from 'date-fns';

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy');
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}
```

**File**: `frontend/src/lib/config/limits.ts`

```typescript
export const LIMITS = {
  MAX_TITLE_LENGTH: 200,
  MAX_DESCRIPTION_LENGTH: 2000,
  MAX_TAGS: 10,
  MAX_SUBTASKS: 50,
  MAX_NOTES: 100,
  // ... etc from backend/docs/perks_limits.md
};
```

### Step 7: Create Auth Context

**File**: `frontend/src/lib/contexts/AuthContext.tsx`

```typescript
'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '@/lib/schemas/user.schema';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // Implementation...

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

---

## Verification Steps

After recreating the lib directory:

### 1. Type Check
```bash
cd frontend
npm run type-check
```
Should pass with no errors.

### 2. Build Test
```bash
npm run build
```
Should complete successfully.

### 3. Development Server
```bash
npm run dev
```
Navigate to http://localhost:3000 and verify:
- No console errors related to missing modules
- Components render without TypeScript errors
- API calls work (after connecting to deployed backend)

### 4. Test Suite
```bash
npm test
```
All tests should pass (may need to update some after lib recreation).

---

## Environment Variables Needed

After backend deployment, create `frontend/.env.local`:

```env
# Backend API URL (from Railway deployment)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1

# Optional: Enable debug mode
NEXT_PUBLIC_DEBUG=false
```

---

## Deployment Checklist

Once lib is recreated and backend is deployed:

- [ ] Update `.gitignore` to allow `frontend/src/lib/`
- [ ] Recreate all lib files (40-45 files)
- [ ] Run `npm run type-check` - should pass
- [ ] Run `npm run build` - should succeed
- [ ] Test locally with deployed backend API
- [ ] Commit lib directory to git
- [ ] Push to GitHub
- [ ] Deploy to Vercel with `NEXT_PUBLIC_API_URL` env var
- [ ] Verify production deployment works

---

## Quick Recovery Commands

When ready to recreate:

```bash
# 1. Fix .gitignore
# Edit .gitignore: change line 13 from "lib/" to "/lib/" or "backend/lib/"

# 2. Create lib directory structure
mkdir -p frontend/src/lib/{api,config,contexts,hooks,schemas,stores,utils}

# 3. Use Claude skill to generate schemas
# /skill multi-stack-code-generator

# 4. Manually create remaining files or use skill to scaffold

# 5. Install any missing dependencies
cd frontend
npm install

# 6. Test build
npm run build

# 7. Commit everything
git add frontend/src/lib
git commit -m "Recreate frontend lib directory with all schemas and utilities"
```

---

## References

- Backend schemas: `backend/src/models/`
- Frontend architecture: `frontend/docs/ARCHITECTURE.md`
- API contracts: `frontend/docs/API_CONTRACTS.md`
- Feature limits: `frontend/docs/perks_limits.md`

---

## Related Issues

- `.gitignore` needs update to prevent this from happening again
- Consider adding lib directory to CI checks to catch missing files
- Backend deployment to Railway should happen first (get API URL)
- Schema sync between frontend/backend should be automated

---

**Next Steps**: Deploy backend to Railway, then return to this document to recreate frontend lib directory.
