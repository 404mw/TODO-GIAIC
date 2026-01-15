/**
 * 404 Not Found Page (T184)
 * Phase 15 - Polish
 *
 * Displayed when a route is not found.
 * Provides navigation back to dashboard.
 */

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-950 px-4">
      <div className="text-center">
        {/* 404 Visual */}
        <div className="mb-8">
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-9xl font-bold text-transparent">
            404
          </span>
        </div>

        {/* Error Message */}
        <h1 className="mb-2 text-3xl font-bold text-white">Page not found</h1>
        <p className="mb-8 max-w-md text-gray-400">
          The page you are looking for does not exist or has been moved. Let us get you back on
          track.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/dashboard/tasks"
            className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/landing"
            className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 font-medium text-white transition-colors hover:bg-white/10"
          >
            Visit Homepage
          </Link>
        </div>

        {/* Help Links */}
        <div className="mt-12">
          <p className="mb-4 text-sm text-gray-500">Looking for something specific?</p>
          <div className="flex flex-wrap justify-center gap-6">
            <Link
              href="/dashboard/tasks"
              className="text-sm text-gray-400 transition-colors hover:text-white"
            >
              Tasks
            </Link>
            <Link
              href="/dashboard/notes"
              className="text-sm text-gray-400 transition-colors hover:text-white"
            >
              Notes
            </Link>
            <Link
              href="/dashboard/achievements"
              className="text-sm text-gray-400 transition-colors hover:text-white"
            >
              Achievements
            </Link>
            <Link
              href="/dashboard/settings"
              className="text-sm text-gray-400 transition-colors hover:text-white"
            >
              Settings
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
