/**
 * T163 — RED test: useSubtasks conditional fetch + camelCase invalidation
 *
 * Tests:
 * 1. useSubtasks(taskId, { enabled: false }) fires zero network requests
 * 2. useCreateSubtask onSuccess invalidates ['subtasks', taskId] (camelCase) not ['subtasks', undefined]
 * 3. useUpdateSubtask onSuccess same camelCase invalidation
 *
 * Acceptance criteria: ≥3 failures before T122/T130 applied; zero failures after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useSubtasks, useCreateSubtask, useUpdateSubtask } from '@/lib/hooks/useSubtasks'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')

const mockApiGet = jest.fn()
const mockApiPost = jest.fn()
;(apiClient as any).get = mockApiGet
;(apiClient as any).post = mockApiPost
;(apiClient as any).put = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T163 — useSubtasks conditional fetch', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('does NOT fire network request when enabled: false', async () => {
    const wrapper = createWrapper()
    renderHook(() => useSubtasks('task-123', { enabled: false }), { wrapper })

    // Wait a tick
    await new Promise((r) => setTimeout(r, 50))

    expect(mockApiGet).not.toHaveBeenCalled()
  })

  it('fires network request when enabled: true (default)', async () => {
    mockApiGet.mockResolvedValue({ data: [] })
    const wrapper = createWrapper()
    renderHook(() => useSubtasks('task-123'), { wrapper })

    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith(
        '/tasks/task-123/subtasks',
        expect.anything()
      )
    })
  })
})

describe('T163 — useCreateSubtask camelCase invalidation', () => {
  it('invalidates ["subtasks", taskId] with camelCase taskId after create', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    })
    const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries')

    mockApiPost.mockResolvedValue({ data: { id: 'sub-new', task_id: 'task-123', title: 'New' } })

    const wrapper = ({ children }: { children: React.ReactNode }) =>
      React.createElement(QueryClientProvider, { client: queryClient }, children)

    const { result } = renderHook(() => useCreateSubtask(), { wrapper })

    await result.current.mutateAsync({ taskId: 'task-123', title: 'New subtask' } as any)

    await waitFor(() => {
      // Should invalidate with camelCase taskId = 'task-123', NOT task_id = undefined
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['subtasks', 'task-123'],
      })
    })

    // Should NOT invalidate with undefined (bug: variables.task_id would be undefined)
    const callsWithUndefined = invalidateSpy.mock.calls.filter(
      (call) => JSON.stringify(call[0]) === JSON.stringify({ queryKey: ['subtasks', undefined] })
    )
    expect(callsWithUndefined).toHaveLength(0)
  })
})

describe('T163 — useUpdateSubtask camelCase invalidation', () => {
  it('invalidates ["subtasks", taskId] with camelCase taskId after update', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    })
    const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries')

    ;(apiClient as any).put = jest.fn().mockResolvedValue({ data: { id: 'sub-1', task_id: 'task-123', title: 'Updated', completed: true } })

    const wrapper = ({ children }: { children: React.ReactNode }) =>
      React.createElement(QueryClientProvider, { client: queryClient }, children)

    const { result } = renderHook(() => useUpdateSubtask(), { wrapper })

    await result.current.mutateAsync({ id: 'sub-1', taskId: 'task-123', completed: true } as any)

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['subtasks', 'task-123'],
      })
    })

    // Should NOT invalidate with undefined
    const callsWithUndefined = invalidateSpy.mock.calls.filter(
      (call) => JSON.stringify(call[0]) === JSON.stringify({ queryKey: ['subtasks', undefined] })
    )
    expect(callsWithUndefined).toHaveLength(0)
  })
})
