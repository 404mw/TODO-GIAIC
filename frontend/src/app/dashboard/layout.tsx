'use client'

import { useEffect, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/lib/hooks/useAuth'
import { Loader2 } from 'lucide-react'

/**
 * Dashboard Layout
 *
 * Protected layout for all dashboard routes
 * Redirects to login if user is not authenticated
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    // If not loading and no user, redirect to login
    if (!isLoading && !user) {
      // Encode current path as redirect parameter
      const redirect = encodeURIComponent(pathname)
      router.push(`/login?redirect=${redirect}`)
    }
  }, [user, isLoading, router, pathname])

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600 dark:text-purple-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  // If no user after loading, show nothing (redirect is in progress)
  if (!user) {
    return null
  }

  // User is authenticated, render dashboard
  return <>{children}</>
}
