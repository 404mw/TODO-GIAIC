'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

/**
 * OAuth Callback Page (Deprecated)
 *
 * This page is no longer used. The application now uses Google Sign-In SDK
 * with ID token authentication instead of OAuth authorization code flow.
 *
 * This page exists only to redirect old bookmarks/links to the login page.
 * For proper authentication, users should visit /login directly.
 */
export default function OAuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to login page
    // Users should use /login which has Google Sign-In SDK integration
    router.replace('/login')
  }, [router])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-8">
          <Loader2 className="h-16 w-16 animate-spin text-purple-600 dark:text-purple-400 mx-auto mb-6" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Redirecting...
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Redirecting you to the login page
          </p>
        </div>
      </div>
    </div>
  )
}
