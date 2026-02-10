/**
 * Dashboard Error Boundary (T183)
 * Phase 15 - Polish
 *
 * Handles errors within the dashboard routes.
 * Keeps sidebar visible for navigation.
 */

'use client'

import { useEffect } from 'react'
import Link from 'next/link'

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function DashboardError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log the error for debugging
    console.error('Dashboard error:', error)
  }, [error])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4">
      <div className="text-center">
        {/* Error Icon */}
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10">
          <svg
            className="h-8 w-8 text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        {/* Error Message */}
        <h2 className="mb-2 text-2xl font-bold text-white">Something went wrong</h2>
        <p className="mb-6 max-w-md text-gray-400">
          We had trouble loading this section. Please try again.
        </p>

        {/* Error Details (development only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-6 max-w-lg overflow-hidden rounded-lg border border-white/10 bg-white/5 p-4 text-left">
            <p className="mb-2 text-sm font-medium text-red-400">Error Details:</p>
            <pre className="overflow-x-auto text-xs text-gray-400">
              {error.message}
            </pre>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-4">
          <button
            onClick={reset}
            className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-5 py-2 text-sm font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
          >
            Try Again
          </button>
          <Link
            href="/dashboard/tasks"
            className="rounded-lg border border-white/20 bg-white/5 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-white/10"
          >
            Back to Tasks
          </Link>
        </div>
      </div>
    </div>
  )
}
