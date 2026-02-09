/**
 * Global Error Boundary (T183, T185)
 * Phase 15 - Polish
 *
 * Handles unexpected errors at the root level.
 * Provides user-friendly error message and recovery options.
 */

'use client'

import { useEffect } from 'react'

interface ErrorProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log the error for debugging
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-950 px-4">
      <div className="text-center">
        {/* Error Icon */}
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-500/10">
          <svg
            className="h-10 w-10 text-red-400"
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
        <h1 className="mb-2 text-3xl font-bold text-white">Something went wrong</h1>
        <p className="mb-8 max-w-md text-gray-400">
          We encountered an unexpected error. Please try again, or contact support if the problem
          persists.
        </p>

        {/* Error Details (development only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-8 max-w-lg overflow-hidden rounded-lg border border-white/10 bg-white/5 p-4 text-left">
            <p className="mb-2 text-sm font-medium text-red-400">Error Details:</p>
            <pre className="overflow-x-auto text-xs text-gray-400">
              {error.message}
              {error.digest && `\n\nDigest: ${error.digest}`}
            </pre>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-4">
          <button
            onClick={reset}
            className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
          >
            Try Again
          </button>
          <a
            href="/dashboard/tasks"
            className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 font-medium text-white transition-colors hover:bg-white/10"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
