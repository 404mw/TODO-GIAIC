/**
 * T166 — RED test: mark-notification-as-read endpoint
 *
 * Tests:
 * 1. Mark-as-read calls PATCH /notifications/{id}/read (path-based)
 * 2. PATCH /notifications/{id} with { read: true } body MUST NOT be called
 * 3. No body is sent with the read endpoint
 *
 * Acceptance criteria: detects wrong endpoint before T129; zero wrong-endpoint failures after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useMarkNotificationRead } from '@/lib/hooks/useNotifications'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')

const mockApiPatch = jest.fn()
;(apiClient as any).patch = mockApiPatch
;(apiClient as any).get = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T166 — mark-notification-as-read endpoint', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('calls PATCH /notifications/{id}/read (path-based action)', async () => {
    mockApiPatch.mockResolvedValue(undefined)

    const wrapper = createWrapper()
    const { result } = renderHook(() => useMarkNotificationRead(), { wrapper })

    await result.current.mutateAsync('notif-1')

    await waitFor(() => {
      expect(mockApiPatch).toHaveBeenCalled()
      const firstCall = mockApiPatch.mock.calls[0]
      expect(firstCall[0]).toBe('/notifications/notif-1/read')
    })
  })

  it('does NOT call PATCH /notifications/{id} with { read: true } body', async () => {
    mockApiPatch.mockResolvedValue(undefined)

    const wrapper = createWrapper()
    const { result } = renderHook(() => useMarkNotificationRead(), { wrapper })

    await result.current.mutateAsync('notif-1')

    await waitFor(() => expect(mockApiPatch).toHaveBeenCalled())

    // Must not call the wrong endpoint (path without /read suffix)
    const wrongCalls = mockApiPatch.mock.calls.filter(([path, body]: [string, unknown]) => {
      const pathMatch = path === '/notifications/notif-1'
      const bodyMatch =
        body !== null &&
        typeof body === 'object' &&
        (body as Record<string, unknown>).read === true
      return pathMatch && bodyMatch
    })
    expect(wrongCalls).toHaveLength(0)
  })

  it('calls the /read endpoint with no meaningful body', async () => {
    mockApiPatch.mockResolvedValue(undefined)

    const wrapper = createWrapper()
    const { result } = renderHook(() => useMarkNotificationRead(), { wrapper })

    await result.current.mutateAsync('notif-2')

    await waitFor(() => {
      const call = mockApiPatch.mock.calls[0]
      const path = call[0]
      expect(path).toBe('/notifications/notif-2/read')
      // Body should be empty/undefined/null (not { read: true })
      const body = call[1]
      expect(body).not.toEqual({ read: true })
    })
  })
})
