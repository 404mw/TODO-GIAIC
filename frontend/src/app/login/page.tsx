/**
 * Login Page
 *
 * Handles user authentication via Google OAuth
 */

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuth } from '@/lib/contexts/AuthContext'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const { login, isAuthenticated, isLoading, error } = useAuth()

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  const handleGoogleLogin = async () => {
    try {
      await login()
    } catch (err) {
      console.error('Login error:', err)
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-900 to-black">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated) {
    return null // Will redirect via useEffect
  }

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-gray-900 to-black">
      {/* Header */}
      <header className="fixed top-0 z-50 w-full border-b border-white/10 bg-gray-900/50 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
              <span className="text-lg font-bold text-white">P</span>
            </div>
            <span className="text-xl font-semibold text-white">Perpetua</span>
          </Link>
          <Link
            href="/"
            className="text-sm text-gray-400 transition-colors hover:text-white"
          >
            Back to Home
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 items-center justify-center px-6 pt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Card */}
          <div className="rounded-2xl border border-white/10 bg-gray-900/50 p-8 backdrop-blur-xl">
            {/* Logo and Title */}
            <div className="mb-8 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600">
                <span className="text-3xl font-bold text-white">P</span>
              </div>
              <h1 className="mb-2 text-2xl font-bold text-white">
                Welcome to Perpetua Flow
              </h1>
              <p className="text-sm text-gray-400">
                Sign in to manage your tasks and boost productivity
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mb-6 rounded-lg border border-red-500/20 bg-red-500/10 p-4"
              >
                <p className="text-sm text-red-400">
                  {error.message || 'Authentication failed. Please try again.'}
                </p>
              </motion.div>
            )}

            {/* Google Sign In Button */}
            <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="group relative w-full overflow-hidden rounded-lg border border-white/10 bg-white p-3 font-medium text-gray-900 transition-all hover:border-white/20 hover:shadow-lg hover:shadow-white/5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center justify-center gap-3">
                {/* Google Icon */}
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span>Continue with Google</span>
              </div>
            </button>

            {/* Divider */}
            <div className="my-6 flex items-center gap-3">
              <div className="h-px flex-1 bg-white/10" />
              <span className="text-xs text-gray-500">OR</span>
              <div className="h-px flex-1 bg-white/10" />
            </div>

            {/* Free Tier Message */}
            <div className="rounded-lg border border-blue-500/20 bg-blue-500/10 p-4 text-center">
              <p className="text-sm text-blue-300">
                <span className="font-semibold">Free forever tier available!</span>
                <br />
                No credit card required to get started.
              </p>
            </div>

            {/* Legal Links */}
            <div className="mt-6 text-center text-xs text-gray-500">
              By signing in, you agree to our{' '}
              <Link href="/terms" className="text-gray-400 hover:text-white">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-gray-400 hover:text-white">
                Privacy Policy
              </Link>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-6 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <span className="text-gray-400">
              Sign up automatically when you sign in with Google
            </span>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
