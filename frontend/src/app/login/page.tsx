'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Chrome, AlertCircle, Loader2, CheckCircle } from 'lucide-react'
import { oauthService, getOAuthError, OAuthError } from '@/lib/services/oauth.service'
import { useAuth } from '@/lib/hooks/useAuth'

/**
 * Login Page Content
 *
 * Handles search params and displays login form
 */
function LoginPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, isLoading: authLoading } = useAuth()

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const redirectTo = searchParams?.get('redirect') || '/dashboard'
  const errorParam = searchParams?.get('error')

  useEffect(() => {
    // If already authenticated, redirect to dashboard
    if (!authLoading && user) {
      router.push(redirectTo)
    }

    // Check for OAuth error in URL
    const oauthError = getOAuthError()
    if (oauthError) {
      setError(getErrorMessage(oauthError))
    } else if (errorParam) {
      setError(getErrorMessage(errorParam))
    }
  }, [user, authLoading, router, redirectTo, errorParam])

  const handleGoogleLogin = () => {
    try {
      setIsLoading(true)
      setError(null)
      oauthService.initiateGoogleLogin(redirectTo)
    } catch (err) {
      console.error('Failed to initiate Google login:', err)
      setError('Failed to start sign-in process. Please try again.')
      setIsLoading(false)
    }
  }

  function getErrorMessage(error: string): string {
    switch (error) {
      case OAuthError.CANCELLED:
        return 'Sign-in was cancelled. Please try again.'
      case OAuthError.FAILED:
      case 'auth_failed':
        return 'Authentication failed. Please try again.'
      case OAuthError.NETWORK_ERROR:
        return 'Network error. Please check your connection and try again.'
      case OAuthError.INVALID_STATE:
        return 'Invalid authentication state. Please try again.'
      default:
        return 'An error occurred during sign-in. Please try again.'
    }
  }

  // Show loading while checking auth status
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600 dark:text-purple-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600">
                <CheckCircle className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Perpetua
              </span>
            </Link>
            <Link
              href="/"
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Login Card */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-8">
            {/* Logo and Heading */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 mb-4">
                <CheckCircle className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Welcome to Perpetua
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Sign in to start managing your tasks
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
            )}

            {/* Google Sign-In Button */}
            <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 hover:border-purple-600 dark:hover:border-purple-500 hover:bg-gray-50 dark:hover:bg-gray-750 text-gray-900 dark:text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <Chrome className="h-5 w-5 text-[#4285F4]" />
                  <span>Continue with Google</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className="my-6 flex items-center gap-4">
              <div className="flex-1 h-px bg-gray-200 dark:bg-gray-800" />
              <span className="text-xs text-gray-500 dark:text-gray-400">OR</span>
              <div className="flex-1 h-px bg-gray-200 dark:bg-gray-800" />
            </div>

            {/* Free Tier CTA */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
              <p className="text-sm font-medium text-purple-900 dark:text-purple-100 mb-2">
                ✨ Start completely free
              </p>
              <p className="text-xs text-purple-700 dark:text-purple-300">
                No credit card required. Get 50 active tasks, streak tracking, focus mode, and more absolutely free.
              </p>
            </div>

            {/* Legal Links */}
            <div className="mt-6 text-center text-xs text-gray-500 dark:text-gray-400">
              By continuing, you agree to our{' '}
              <Link href="/terms" className="text-purple-600 dark:text-purple-400 hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-purple-600 dark:text-purple-400 hover:underline">
                Privacy Policy
              </Link>
            </div>
          </div>

          {/* Help Text */}
          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Need help?{' '}
            <Link href="/contact" className="text-purple-600 dark:text-purple-400 hover:underline">
              Contact Support
            </Link>
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © {new Date().getFullYear()} Perpetua. Open Source on{' '}
            <a
              href="https://github.com/404mw/perpetua"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 dark:text-purple-400 hover:underline"
            >
              GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}

/**
 * Login Page
 *
 * Provides Google OAuth authentication
 * Shows error messages and handles redirects
 */
export default function LoginPage() {
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
      <LoginPageContent />
    </Suspense>
  )
}
