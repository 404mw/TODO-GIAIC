/**
 * T161 — RED test: useForceCompleteTask endpoint + response schema
 *
 * Tests:
 * 1. Calls POST /tasks/{id}/force-complete with { version } in body
 * 2. Response parsed against ForceCompleteResponseSchema
 * 3. Confirms no useCompleteTask or useAutoCompleteTask export exists
 *
 * Acceptance criteria: ≥2 failures before T123; zero failures after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import * as useTasks from '@/lib/hooks/useTasks'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')

const mockApiPost = jest.fn()
;(apiClient as any).post = mockApiPost
;(apiClient as any).get = jest.fn()
;(apiClient as any).put = jest.fn()
;(apiClient as any).patch = jest.fn()
;(apiClient as any).delete = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T161 — useForceCompleteTask', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('does NOT export useCompleteTask (non-existent endpoint)', () => {
    expect((useTasks as any).useCompleteTask).toBeUndefined()
  })

  it('does NOT export useAutoCompleteTask (non-existent endpoint)', () => {
    expect((useTasks as any).useAutoCompleteTask).toBeUndefined()
  })

  it('exports useForceCompleteTask', () => {
    expect(typeof (useTasks as any).useForceCompleteTask).toBe('function')
  })

  it('calls POST /tasks/{id}/force-complete with { version } body', async () => {
    const taskId = 'task-abc'
    const version = 3

    mockApiPost.mockResolvedValue({
      data: {
        task: {
          id: taskId,
          user_id: 'user-1',
          template_id: null,
          title: 'Done task',
          description: '',
          priority: 'medium',
          due_date: null,
          estimated_duration: null,
          focus_time_seconds: 0,
          completed: true,
          completed_at: '2026-01-01T00:00:00Z',
          completed_by: 'force',
          hidden: false,
          archived: false,
          subtask_count: 0,
          subtask_completed_count: 0,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          version: 4,
        },
        unlocked_achievements: [],
        streak: 5,
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => (useTasks as any).useForceCompleteTask(), { wrapper })

    await result.current.mutateAsync({ taskId, version })

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith(
        `/tasks/${taskId}/force-complete`,
        { version },
        expect.anything() // schema
      )
    })
  })

  it('response includes task, unlocked_achievements[], and streak', async () => {
    const taskId = 'task-xyz'

    const mockResponse = {
      data: {
        task: {
          id: taskId,
          user_id: 'user-1',
          template_id: null,
          title: 'Done',
          description: '',
          priority: 'medium',
          due_date: null,
          estimated_duration: null,
          focus_time_seconds: 0,
          completed: true,
          completed_at: '2026-01-01T00:00:00Z',
          completed_by: 'force',
          hidden: false,
          archived: false,
          subtask_count: 0,
          subtask_completed_count: 0,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          version: 2,
        },
        unlocked_achievements: [{ id: 'ach-1', name: 'First Task!', perk_type: 'max_tasks', perk_value: 10 }],
        streak: 3,
      },
    }

    mockApiPost.mockResolvedValue(mockResponse)

    const wrapper = createWrapper()
    const { result } = renderHook(() => (useTasks as any).useForceCompleteTask(), { wrapper })

    const response = await result.current.mutateAsync({ taskId, version: 1 })

    expect(response.data.task.id).toBe(taskId)
    expect(response.data.unlocked_achievements).toHaveLength(1)
    expect(response.data.streak).toBe(3)
  })
})
