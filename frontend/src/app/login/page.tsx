'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Chrome, AlertCircle, Loader2, CheckCircle } from 'lucide-react'
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { oauthService } from '@/lib/services/oauth.service'
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

  useEffect(() => {
    // If already authenticated, redirect to dashboard
    if (!authLoading && user) {
      router.push(redirectTo)
    }
  }, [user, authLoading, router, redirectTo])

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      setError('No credential received from Google')
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      // Send ID token to backend
      await oauthService.authenticateWithGoogle(credentialResponse.credential)

      // Redirect to dashboard or specified redirect path
      router.push(redirectTo)
    } catch (err) {
      console.error('Google authentication failed:', err)
      setError('Authentication failed. Please try again.')
      setIsLoading(false)
    }
  }

  const handleGoogleError = () => {
    console.error('Google sign-in failed')
    setError('Google sign-in failed. Please try again.')
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
            <div className="w-full">
              {isLoading ? (
                <div className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white font-semibold">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Signing in...</span>
                </div>
              ) : (
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={handleGoogleError}
                    theme="outline"
                    size="large"
                    text="continue_with"
                    width="384"
                  />
                </div>
              )}
            </div>

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
 * Provides Google OAuth authentication with Google Sign-In SDK
 * Shows error messages and handles redirects
 */
export default function LoginPage() {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID

  if (!clientId) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-gray-900 dark:text-white font-semibold mb-2">
            Configuration Error
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Google OAuth is not configured. Please set NEXT_PUBLIC_GOOGLE_CLIENT_ID environment variable.
          </p>
        </div>
      </div>
    )
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
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
    </GoogleOAuthProvider>
  )
}
