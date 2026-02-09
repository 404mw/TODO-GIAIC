'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState, useEffect, createContext, useContext } from 'react'
import { CommandPalette } from '@/components/ui/CommandPalette'
import { OnboardingTour } from '@/components/onboarding/OnboardingTour'
import { AuthProvider } from '@/lib/contexts/AuthContext'

/**
 * MSW Ready context - allows components to know when MSW is initialized
 */
const MSWReadyContext = createContext(false)
export const useMSWReady = () => useContext(MSWReadyContext)

/**
 * Application providers wrapper
 *
 * Sets up:
 * - TanStack Query (React Query) for server state management
 * - MSW (Mock Service Worker) for API mocking in development
 * - React Query Devtools in development mode
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // Track MSW readiness - in production, always ready
  const [mswReady, setMswReady] = useState(process.env.NODE_ENV === 'production')

  // Create query client with queries disabled until MSW is ready (dev only)
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Default query options
            staleTime: 1000 * 60 * 5, // 5 minutes
            gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
            refetchOnWindowFocus: true,
            refetchOnReconnect: true,
            retry: 1,
          },
          mutations: {
            // Default mutation options
            retry: 1,
          },
        },
      })
  )

  useEffect(() => {
    // Initialize MSW in development mode (client-side only)
    if (process.env.NODE_ENV === 'production') {
      return
    }

    let mounted = true

    const initMSW = async () => {
      try {
        const { startMSW } = await import('@/mocks/browser')
        await startMSW({
          onUnhandledRequest: 'warn',
        })
        if (mounted) {
          setMswReady(true)
        }
      } catch (error) {
        console.error('[MSW] Failed to initialize:', error)
        if (mounted) {
          setMswReady(true) // Continue anyway
        }
      }
    }

    initMSW()

    return () => {
      mounted = false
    }
  }, [])

  // Refetch queries once MSW is ready
  useEffect(() => {
    if (mswReady && process.env.NODE_ENV !== 'production') {
      // Invalidate all queries to trigger refetch now that MSW is ready
      queryClient.invalidateQueries()
    }
  }, [mswReady, queryClient])

  return (
    <MSWReadyContext.Provider value={mswReady}>
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
    </MSWReadyContext.Provider>
  )
}
