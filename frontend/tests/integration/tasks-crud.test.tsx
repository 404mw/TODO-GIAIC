/**
 * Task CRUD Integration Tests
 *
 * Tests task operations against the apiClient layer:
 * 1. List tasks with pagination
 * 2. Create task with idempotency
 * 3. Update task with version conflict handling
 * 4. Delete task returns tombstone
 * 5. Force complete updates achievements
 */

import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement, type ReactNode } from 'react'
import {
  useTasks,
  useTask,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useForceCompleteTask,
} from '@/lib/hooks/useTasks'
import { ApiError } from '@/lib/api/client'
import { mockTask, mockTaskDetail, paginatedResponse } from './setup'

// Mock the apiClient
jest.mock('@/lib/api/client', () => {
  const actual = jest.requireActual('@/lib/api/client')
  return {
    ...actual,
    apiClient: {
      get: jest.fn(),
      post: jest.fn(),
      patch: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    },
  }
})

import { apiClient } from '@/lib/api/client'

const mockGet = apiClient.get as jest.MockedFunction<typeof apiClient.get>
const mockPost = apiClient.post as jest.MockedFunction<typeof apiClient.post>
const mockPatch = apiClient.patch as jest.MockedFunction<typeof apiClient.patch>
const mockDelete = apiClient.delete as jest.MockedFunction<typeof apiClient.delete>

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })

  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children)
  }

  return { Wrapper, queryClient }
}

describe('Task CRUD Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('1. List tasks with pagination', () => {
    it('should fetch paginated task list', async () => {
      const taskList = [
        mockTask,
        { ...mockTask, id: '00000000-0000-4000-a000-000000000011', title: 'Second task' },
      ]
      mockGet.mockResolvedValue(paginatedResponse(taskList, 2))

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useTasks(), { wrapper: Wrapper })

      await waitFor(() => expect(result.current.isSuccess).toBe(true))

      expect(mockGet).toHaveBeenCalledWith('/tasks', { params: {} })
      expect(result.current.data).toEqual(paginatedResponse(taskList, 2))
    })

    it('should pass filters as query params', async () => {
      mockGet.mockResolvedValue(paginatedResponse([]))

      const { Wrapper } = createWrapper()
      renderHook(
        () => useTasks({ completed: true, priority: 'high', hidden: false }),
        { wrapper: Wrapper }
      )

      await waitFor(() => {
        expect(mockGet).toHaveBeenCalledWith('/tasks', {
          params: { completed: true, priority: 'high', hidden: false },
        })
      })
    })

    it('should fetch single task detail', async () => {
      mockGet.mockResolvedValue(mockTaskDetail)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useTask(mockTask.id), { wrapper: Wrapper })

      await waitFor(() => expect(result.current.isSuccess).toBe(true))

      expect(mockGet).toHaveBeenCalledWith(`/tasks/${mockTask.id}`)
      expect(result.current.data).toEqual(mockTaskDetail)
    })
  })

  describe('2. Create task with idempotency', () => {
    it('should create task and invalidate list cache', async () => {
      const newTask = { ...mockTask, id: '00000000-0000-4000-a000-000000000099', title: 'New task' }
      mockPost.mockResolvedValue(newTask)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useCreateTask(), { wrapper: Wrapper })

      await act(async () => {
        await result.current.mutateAsync({ title: 'New task' })
      })

      expect(mockPost).toHaveBeenCalledWith(
        '/tasks',
        { title: 'New task' },
        expect.objectContaining({ idempotencyKey: expect.any(String) })
      )
    })

    it('should pass idempotency key for safe retries', async () => {
      mockPost.mockResolvedValue(mockTask)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useCreateTask(), { wrapper: Wrapper })

      await act(async () => {
        await result.current.mutateAsync({ title: 'Test' })
      })

      // Verify idempotency key was included
      const callArgs = mockPost.mock.calls[0]
      expect(callArgs[2]).toHaveProperty('idempotencyKey')
      expect(typeof callArgs[2]!.idempotencyKey).toBe('string')
    })
  })

  describe('3. Update task with version conflict handling', () => {
    it('should update task via PATCH', async () => {
      const updated = { ...mockTask, title: 'Updated title', version: 2 }
      mockPatch.mockResolvedValue(updated)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useUpdateTask(), { wrapper: Wrapper })

      await act(async () => {
        await result.current.mutateAsync({
          id: mockTask.id,
          input: { title: 'Updated title', version: 1 },
        })
      })

      expect(mockPatch).toHaveBeenCalledWith(
        `/tasks/${mockTask.id}`,
        { title: 'Updated title', version: 1 },
        expect.objectContaining({ idempotencyKey: expect.any(String) })
      )
    })

    it('should handle version conflict error (409)', async () => {
      const conflictError = new ApiError(
        { code: 'CONFLICT', message: 'Version conflict', details: [] },
        409
      )
      mockPatch.mockRejectedValue(conflictError)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useUpdateTask(), { wrapper: Wrapper })

      await act(async () => {
        try {
          await result.current.mutateAsync({
            id: mockTask.id,
            input: { title: 'Conflict update', version: 1 },
          })
        } catch (err) {
          expect(err).toBeInstanceOf(ApiError)
          expect((err as ApiError).code).toBe('CONFLICT')
        }
      })
    })
  })

  describe('4. Delete task returns tombstone', () => {
    it('should delete task and return tombstone data', async () => {
      const deleteResponse = {
        tombstoneId: '00000000-0000-4000-a000-000000000099',
        recoverableUntil: '2025-06-08T10:00:00Z',
      }
      mockDelete.mockResolvedValue(deleteResponse)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useDeleteTask(), { wrapper: Wrapper })

      let response: any
      await act(async () => {
        response = await result.current.mutateAsync(mockTask.id)
      })

      expect(mockDelete).toHaveBeenCalledWith(`/tasks/${mockTask.id}`)
      expect(response).toEqual(deleteResponse)
    })
  })

  describe('5. Force complete updates achievements', () => {
    it('should force complete task and return completion response', async () => {
      const completionResponse = {
        task: {
          ...mockTaskDetail,
          completed: true,
          completedAt: '2025-06-01T12:00:00Z',
          completedBy: 'force',
        },
        unlockedAchievements: [{ id: 'ach-1', name: 'First Complete', perkType: null, perkValue: null }],
        streak: 5,
      }
      mockPost.mockResolvedValue(completionResponse)

      const { Wrapper } = createWrapper()
      const { result } = renderHook(() => useForceCompleteTask(), { wrapper: Wrapper })

      let response: any
      await act(async () => {
        response = await result.current.mutateAsync({ id: mockTask.id, version: 1 })
      })

      expect(mockPost).toHaveBeenCalledWith(
        `/tasks/${mockTask.id}/force-complete`,
        { version: 1 }
      )
      expect(response.unlockedAchievements).toHaveLength(1)
      expect(response.streak).toBe(5)
    })
  })
})
