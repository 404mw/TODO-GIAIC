/**
 * T173 — RED test: Notes standalone migration
 *
 * Tests:
 * 1. useCreateNote() calls POST /api/v1/notes (not task-scoped)
 * 2. useNotes() calls GET /api/v1/notes (no taskId param)
 * 3. useUpdateNote() uses apiClient.patch not apiClient.put
 * 4. useNotes accepts no taskId option
 *
 * Acceptance criteria: ≥3 wrong-endpoint/method failures before T125; zero after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useNotes, useCreateNote, useUpdateNote } from '@/lib/hooks/useNotes'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')

const mockApiGet = jest.fn()
const mockApiPost = jest.fn()
const mockApiPatch = jest.fn()
;(apiClient as any).get = mockApiGet
;(apiClient as any).post = mockApiPost
;(apiClient as any).patch = mockApiPatch
;(apiClient as any).put = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T173 — Notes standalone migration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('useNotes() calls GET /notes (standalone, no taskId)', async () => {
    mockApiGet.mockResolvedValue({ data: [] })

    const wrapper = createWrapper()
    renderHook(() => useNotes(), { wrapper })

    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalledWith('/notes', expect.anything())
    })
  })

  it('useNotes() does NOT call task-scoped endpoint', async () => {
    mockApiGet.mockResolvedValue({ data: [] })

    const wrapper = createWrapper()
    renderHook(() => useNotes(), { wrapper })

    await waitFor(() => {
      expect(mockApiGet).toHaveBeenCalled()
    })

    // Ensure no task-scoped path was called
    const calls = mockApiGet.mock.calls
    const taskScopedCalls = calls.filter(([path]: [string]) =>
      path.includes('/tasks/') && path.includes('/notes')
    )
    expect(taskScopedCalls).toHaveLength(0)
  })

  it('useCreateNote() calls POST /notes (standalone)', async () => {
    mockApiPost.mockResolvedValue({
      data: {
        id: 'note-1',
        user_id: 'u1',
        content: 'Test',
        archived: false,
        voice_url: null,
        voice_duration_seconds: null,
        transcription_status: null,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useCreateNote(), { wrapper })

    await result.current.mutateAsync({ content: 'Test note' } as any)

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith('/notes', expect.anything(), expect.anything())
    })

    // Should NOT call task-scoped endpoint
    const taskScopedCalls = mockApiPost.mock.calls.filter(([path]: [string]) =>
      path.includes('/tasks/')
    )
    expect(taskScopedCalls).toHaveLength(0)
  })

  it('useUpdateNote() uses PATCH not PUT', async () => {
    mockApiPatch.mockResolvedValue({
      data: {
        id: 'note-1',
        user_id: 'u1',
        content: 'Updated',
        archived: false,
        voice_url: null,
        voice_duration_seconds: null,
        transcription_status: null,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpdateNote(), { wrapper })

    await result.current.mutateAsync({ id: 'note-1', content: 'Updated' } as any)

    await waitFor(() => {
      expect(mockApiPatch).toHaveBeenCalledWith(
        '/notes/note-1',
        expect.anything(),
        expect.anything()
      )
    })

    // PUT should NOT have been called
    expect((apiClient as any).put).not.toHaveBeenCalledWith(
      '/notes/note-1',
      expect.anything(),
      expect.anything()
    )
  })
})
