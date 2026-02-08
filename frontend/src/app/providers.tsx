'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'
import { CommandPalette } from '@/components/ui/CommandPalette'
import { OnboardingTour } from '@/components/onboarding/OnboardingTour'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AuthProvider } from '@/lib/contexts/AuthContext'
import { ApiError } from '@/lib/api/client'
import { showApiError } from '@/lib/hooks/useToast'

/** Error codes that should NOT be retried automatically */
const NON_RETRYABLE_CODES = new Set([
  'UNAUTHORIZED',
  'TOKEN_EXPIRED',
  'NOT_FOUND',
  'FORBIDDEN',
  'TIER_REQUIRED',
  'INSUFFICIENT_CREDITS',
])

/**
 * Application providers wrapper
 *
 * Sets up:
 * - TanStack Query with global error handling
 * - ErrorBoundary for rendering errors
 * - React Query Devtools in development mode
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            gcTime: 1000 * 60 * 10, // 10 minutes
            refetchOnWindowFocus: true,
            refetchOnReconnect: true,
            retry: (failureCount, error) => {
              if (error instanceof ApiError && NON_RETRYABLE_CODES.has(error.code)) {
                return false
              }
              return failureCount < 3
            },
          },
          mutations: {
            onError: (error) => {
              showApiError(error)
            },
          },
        },
      })
  )

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {children}
          <CommandPalette />
          <OnboardingTour autoStart />
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-right" />
          )}
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
