/**
 * Integration Test Setup
 *
 * Provides test utilities for integration tests:
 * - renderWithProviders: wraps components with QueryClientProvider
 * - Mock fixtures matching current backend schemas
 * - apiClient mock factory
 */

import { render, type RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement, type ReactElement } from 'react'
import type { Task, TaskDetail } from '@/lib/schemas/task.schema'
import type { UserResponse } from '@/lib/api/user'
import type { SubTask } from '@/lib/schemas/subtask.schema'
import type { Note } from '@/lib/schemas/note.schema'

// ---------------------------------------------------------------------------
// renderWithProviders
// ---------------------------------------------------------------------------

interface ProviderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient
}

/**
 * Create a fresh QueryClient for testing (no retries, no caching)
 */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })
}

/**
 * Render a component wrapped with QueryClientProvider.
 * Returns the render result plus the queryClient for assertions.
 */
export function renderWithProviders(
  ui: ReactElement,
  options: ProviderOptions = {}
) {
  const { queryClient = createTestQueryClient(), ...renderOptions } = options

  function Wrapper({ children }: { children: React.ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children)
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  }
}

// ---------------------------------------------------------------------------
// Mock Fixtures (matching current backend schemas)
// ---------------------------------------------------------------------------

export const mockUser: UserResponse = {
  id: '00000000-0000-4000-a000-000000000001',
  email: 'test@example.com',
  name: 'Test User',
  avatar_url: null,
  timezone: 'UTC',
  tier: 'free',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-06-01T00:00:00Z',
}

export const mockTask: Task = {
  id: '00000000-0000-4000-a000-000000000010',
  title: 'Test task',
  description: 'A test task description',
  priority: 'medium',
  dueDate: null,
  estimatedDuration: null,
  focusTimeSeconds: 0,
  completed: false,
  completedAt: null,
  completedBy: null,
  hidden: false,
  archived: false,
  templateId: null,
  subtaskCount: 0,
  subtaskCompletedCount: 0,
  version: 1,
  tags: [],
  recurrence: null,
  createdAt: '2025-06-01T10:00:00Z',
  updatedAt: '2025-06-01T10:00:00Z',
}

export const mockTaskDetail: TaskDetail = {
  id: mockTask.id,
  title: mockTask.title,
  description: mockTask.description,
  priority: mockTask.priority,
  dueDate: mockTask.dueDate,
  estimatedDuration: mockTask.estimatedDuration,
  focusTimeSeconds: mockTask.focusTimeSeconds,
  completed: mockTask.completed,
  completedAt: mockTask.completedAt,
  completedBy: mockTask.completedBy,
  hidden: mockTask.hidden,
  archived: mockTask.archived,
  templateId: mockTask.templateId,
  version: mockTask.version,
  tags: [],
  recurrence: null,
  createdAt: mockTask.createdAt,
  updatedAt: mockTask.updatedAt,
  subtasks: [],
  reminders: [],
}

export const mockSubTask: SubTask = {
  id: '00000000-0000-4000-a000-000000000020',
  taskId: mockTask.id,
  title: 'Test subtask',
  completed: false,
  completedAt: null,
  orderIndex: 0,
  source: 'user',
  createdAt: '2025-06-01T10:00:00Z',
  updatedAt: '2025-06-01T10:00:00Z',
}

export const mockNote: Note = {
  id: '00000000-0000-4000-a000-000000000030',
  content: 'Some note content',
  archived: false,
  voiceUrl: null,
  voiceDurationSeconds: null,
  transcriptionStatus: null,
  createdAt: '2025-06-01T10:00:00Z',
  updatedAt: '2025-06-01T10:00:00Z',
}

// ---------------------------------------------------------------------------
// Paginated response helper
// ---------------------------------------------------------------------------

export function paginatedResponse<T>(data: T[], total?: number) {
  return {
    data,
    pagination: {
      offset: 0,
      limit: 20,
      total: total ?? data.length,
      hasMore: false,
    },
  }
}
