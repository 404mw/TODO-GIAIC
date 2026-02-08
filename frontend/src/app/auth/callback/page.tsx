/**
 * OAuth Callback Page
 *
 * Handles the redirect from Google OAuth.
 * Extracts the ID token from URL hash and completes authentication.
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/contexts/AuthContext'
import Link from 'next/link'

type CallbackState = 'processing' | 'success' | 'error'

export default function AuthCallbackPage() {
  const router = useRouter()
  const { handleGoogleCallback } = useAuth()
  const [state, setState] = useState<CallbackState>('processing')
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Google OAuth returns the ID token in the URL hash fragment
        // Format: #id_token=...&state=...&other_params=...
        const hash = window.location.hash.substring(1) // Remove leading #
        const params = new URLSearchParams(hash)

        const idToken = params.get('id_token')
        const state = params.get('state')
        const error = params.get('error')

        // Check for OAuth errors
        if (error) {
          const errorDescription = params.get('error_description') || 'Authentication failed'
          throw new Error(errorDescription)
        }

        // Validate ID token exists
        if (!idToken) {
          throw new Error('No ID token received from Google')
        }

        // Validate state for CSRF protection
        const savedState = sessionStorage.getItem('oauth_state')
        if (state !== savedState) {
          throw new Error('Invalid state parameter - possible CSRF attack')
        }

        // Complete authentication
        await handleGoogleCallback(idToken)

        setState('success')

        // Redirect to dashboard after a brief delay
        setTimeout(() => {
          router.push('/dashboard')
        }, 1500)
      } catch (err) {
        console.error('OAuth callback error:', err)
        setState('error')
        setErrorMessage(err instanceof Error ? err.message : 'Authentication failed')

        // Clear OAuth session data
        sessionStorage.removeItem('oauth_state')
        sessionStorage.removeItem('oauth_nonce')
      }
    }

    handleCallback()
  }, [handleGoogleCallback, router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black px-6">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-8 backdrop-blur-xl">
          {/* Processing State */}
          {state === 'processing' && (
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
              <h2 className="text-xl font-semibold text-white">
                Completing Sign In...
              </h2>
              <p className="text-sm text-gray-400">
                Please wait while we verify your account
              </p>
            </div>
          )}

          {/* Success State */}
          {state === 'success' && (
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20">
                <svg
                  className="h-6 w-6 text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white">
                Success!
              </h2>
              <p className="text-sm text-gray-400">
                Redirecting to your dashboard...
              </p>
            </div>
          )}

          {/* Error State */}
          {state === 'error' && (
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/20">
                <svg
                  className="h-6 w-6 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white">
                Authentication Failed
              </h2>
              <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
                <p className="text-sm text-red-400">
                  {errorMessage}
                </p>
              </div>
              <Link
                href="/login"
                className="mt-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
              >
                Try Again
              </Link>
              <Link
                href="/"
                className="text-sm text-gray-400 hover:text-white"
              >
                Back to Home
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
