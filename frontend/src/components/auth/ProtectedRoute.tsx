/**
 * Protected Route Component
 *
 * Wraps pages/components that require authentication.
 * Redirects to login if user is not authenticated.
 */

'use client'

import { useEffect, type ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/contexts/AuthContext'

interface ProtectedRouteProps {
  children: ReactNode
  /** Optional loading component to show while checking auth */
  loadingComponent?: ReactNode
  /** Optional redirect path (defaults to /login) */
  redirectTo?: string
}

export function ProtectedRoute({
  children,
  loadingComponent,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Save the current path for post-login redirect
      const currentPath = window.location.pathname + window.location.search
      if (currentPath !== redirectTo) {
        sessionStorage.setItem('auth_redirect', currentPath)
      }
      router.push(redirectTo)
    }
  }, [isLoading, isAuthenticated, router, redirectTo])

  // Show loading state while checking authentication
  if (isLoading) {
    if (loadingComponent) {
      return <>{loadingComponent}</>
    }

    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render children if not authenticated (will redirect via useEffect)
  if (!isAuthenticated) {
    return null
  }

  // User is authenticated, render the protected content
  return <>{children}</>
}

/**
 * Higher-order component version for wrapping page components
 *
 * @example
 * ```tsx
 * const ProtectedDashboard = withAuth(DashboardPage)
 * export default ProtectedDashboard
 * ```
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    loadingComponent?: ReactNode
    redirectTo?: string
  }
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute
        loadingComponent={options?.loadingComponent}
        redirectTo={options?.redirectTo}
      >
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}
