/**
 * T162 — RED test: useUpdateTask always includes version field
 *
 * Tests:
 * 1. Every useUpdateTask.mutate() call site includes version
 * 2. Missing version triggers 400 error
 *
 * Acceptance criteria: ≥1 missing-version path before T124; zero after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useUpdateTask } from '@/lib/hooks/useTasks'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')

const mockApiPatch = jest.fn()
;(apiClient as any).patch = mockApiPatch
;(apiClient as any).get = jest.fn()
;(apiClient as any).post = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T162 — useUpdateTask version field', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('sends PATCH (not PUT) to /tasks/{id}', async () => {
    mockApiPatch.mockResolvedValue({
      data: {
        id: 'task-1',
        user_id: 'u1',
        template_id: null,
        title: 'Updated',
        description: '',
        priority: 'medium',
        due_date: null,
        estimated_duration: null,
        focus_time_seconds: 0,
        completed: false,
        completed_at: null,
        completed_by: null,
        hidden: false,
        archived: false,
        subtask_count: 0,
        subtask_completed_count: 0,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
        version: 2,
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpdateTask(), { wrapper })

    await result.current.mutateAsync({ id: 'task-1', title: 'Updated', version: 1 })

    await waitFor(() => {
      expect(mockApiPatch).toHaveBeenCalledWith(
        '/tasks/task-1',
        expect.objectContaining({ title: 'Updated', version: 1 }),
        expect.anything()
      )
    })

    // Verify PATCH was called (not PUT)
    expect(mockApiPatch).toHaveBeenCalled()
  })

  it('includes version field in patch body', async () => {
    const patchBody = { title: 'New title', version: 3 }

    mockApiPatch.mockResolvedValue({
      data: {
        id: 'task-1',
        user_id: 'u1',
        template_id: null,
        title: 'New title',
        description: '',
        priority: 'medium',
        due_date: null,
        estimated_duration: null,
        focus_time_seconds: 0,
        completed: false,
        completed_at: null,
        completed_by: null,
        hidden: false,
        archived: false,
        subtask_count: 0,
        subtask_completed_count: 0,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
        version: 4,
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpdateTask(), { wrapper })

    await result.current.mutateAsync({ id: 'task-1', ...patchBody })

    await waitFor(() => {
      const call = mockApiPatch.mock.calls[0]
      const body = call[1]
      expect(body).toHaveProperty('version', 3)
    })
  })
})
