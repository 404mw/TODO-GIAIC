/**
 * T165 — RED test: subscription upgrade endpoint
 *
 * Tests:
 * 1. useUpgradeSubscription calls POST /subscription/upgrade (not /checkout)
 * 2. Calls do NOT go to /subscription/checkout
 * 3. Calls do NOT go to /subscription/purchase-credits
 *
 * Acceptance criteria: test catches wrong endpoint before T127; zero failures after.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { useUpgradeSubscription } from '@/lib/hooks/useSubscription'
import { apiClient } from '@/lib/api/client'

jest.mock('@/lib/api/client')
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

const mockApiPost = jest.fn()
;(apiClient as any).post = mockApiPost
;(apiClient as any).get = jest.fn()

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T165 — subscription upgrade endpoint', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('useUpgradeSubscription calls POST /subscription/upgrade', async () => {
    mockApiPost.mockResolvedValue({
      data: {
        tier: 'pro',
        status: 'active',
        current_period_end: '2027-01-01T00:00:00Z',
        cancel_at_period_end: false,
        features: {
          max_subtasks: 100,
          max_description_length: 5000,
          voice_notes: true,
          monthly_credits: 100,
        },
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpgradeSubscription(), { wrapper })

    await result.current.mutateAsync()

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith(
        '/subscription/upgrade',
        expect.anything(),
        expect.anything()
      )
    })
  })

  it('does NOT call /subscription/checkout', async () => {
    mockApiPost.mockResolvedValue({
      data: {
        tier: 'pro',
        status: 'active',
        current_period_end: '2027-01-01T00:00:00Z',
        cancel_at_period_end: false,
        features: {
          max_subtasks: 100,
          max_description_length: 5000,
          voice_notes: true,
          monthly_credits: 100,
        },
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpgradeSubscription(), { wrapper })

    await result.current.mutateAsync()

    await waitFor(() => expect(mockApiPost).toHaveBeenCalled())

    const checkoutCalls = mockApiPost.mock.calls.filter(([path]: [string]) =>
      path.includes('/subscription/checkout')
    )
    expect(checkoutCalls).toHaveLength(0)
  })

  it('does NOT call /subscription/purchase-credits', async () => {
    mockApiPost.mockResolvedValue({
      data: {
        tier: 'pro',
        status: 'active',
        current_period_end: '2027-01-01T00:00:00Z',
        cancel_at_period_end: false,
        features: {
          max_subtasks: 100,
          max_description_length: 5000,
          voice_notes: true,
          monthly_credits: 100,
        },
      },
    })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useUpgradeSubscription(), { wrapper })

    await result.current.mutateAsync()

    await waitFor(() => expect(mockApiPost).toHaveBeenCalled())

    const creditCalls = mockApiPost.mock.calls.filter(([path]: [string]) =>
      path.includes('/subscription/purchase-credits')
    )
    expect(creditCalls).toHaveLength(0)
  })
})
