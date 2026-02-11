'use client'

import { Suspense, useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import { oauthService, getOAuthError, OAuthError } from '@/lib/services/oauth.service'
import { useAuth } from '@/lib/hooks/useAuth'
import Link from 'next/link'

/**
 * OAuth Callback Content Component
 * Handles OAuth callback and completes authentication
 */
function OAuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { refetch } = useAuth()

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function handleCallback() {
      try {
        // Check for OAuth error
        const oauthError = getOAuthError()
        if (oauthError) {
          setError(getErrorMessage(oauthError))
          setStatus('error')
          return
        }

        // TODO: Migrate to Google Sign-In SDK + ID token flow
        // Current implementation uses legacy OAuth authorization code flow.
        // According to API.md, the backend expects:
        // POST /api/v1/auth/google/callback with { id_token: string }
        //
        // Migration steps:
        // 1. Integrate Google Sign-In SDK on frontend
        // 2. Get ID token from Google Sign-In
        // 3. Call authService.googleCallback(idToken) instead of handleCallback(code, state)
        // 4. Remove oauthService.initiateGoogleLogin() flow
        // See: https://developers.google.com/identity/gsi/web/guides/overview

        // Get callback parameters
        const code = searchParams?.get('code')
        const state = searchParams?.get('state')

        if (!code || !state) {
          setError('Missing authentication parameters')
          setStatus('error')
          return
        }

        // Exchange code for token (legacy flow)
        await oauthService.handleCallback(code, state)

        // Clear OAuth params from URL
        oauthService.clearCallbackParams()

        // Refetch user data
        await refetch()

        // Success!
        setStatus('success')

        // Redirect to dashboard or specified redirect
        const redirect = searchParams?.get('redirect') || '/dashboard'
        setTimeout(() => {
          router.push(redirect)
        }, 1500)
      } catch (err) {
        console.error('OAuth callback error:', err)
        setError(err instanceof Error ? err.message : 'Authentication failed')
        setStatus('error')
      }
    }

    handleCallback()
  }, [searchParams, refetch, router])

  function getErrorMessage(error: string): string {
    switch (error) {
      case OAuthError.CANCELLED:
        return 'Sign-in was cancelled'
      case OAuthError.FAILED:
        return 'Authentication failed'
      case OAuthError.NETWORK_ERROR:
        return 'Network error occurred'
      case OAuthError.INVALID_STATE:
        return 'Invalid authentication state'
      default:
        return 'An error occurred during sign-in'
    }
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-8">
            <Loader2 className="h-16 w-16 animate-spin text-purple-600 dark:text-purple-400 mx-auto mb-6" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Completing Sign In
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Please wait while we complete your authentication...
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 mb-6">
              <AlertCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Sign In Failed
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {error || 'An error occurred during sign-in'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-700 transition-colors"
              >
                Try Again
              </Link>
              <Link
                href="/"
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-3 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Success
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 mb-6">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Sign In Successful!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Redirecting to your dashboard...
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Please wait</span>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * OAuth Callback Page
 *
 * Handles OAuth callback from Google
 * Exchanges authorization code for access token
 * Redirects to dashboard on success
 */
export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-purple-600 dark:text-purple-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      }
    >
      <OAuthCallbackContent />
    </Suspense>
  )
}
