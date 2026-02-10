'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { CheckCircle, Zap, ArrowRight } from 'lucide-react'
import { useCreditBalance } from '@/lib/hooks/useCredits'

/**
 * Payment Success Content Component
 * Handles search params and displays success message
 */
function PaymentSuccessContent() {
  const searchParams = useSearchParams()
  const { data: balanceData, refetch } = useCreditBalance()
  const [showConfetti, setShowConfetti] = useState(true)

  const sessionId = searchParams.get('session_id')
  const creditsAmount = searchParams.get('credits')

  useEffect(() => {
    // Refetch balance to show updated credits
    refetch()

    // Hide confetti after 3 seconds
    const timer = setTimeout(() => setShowConfetti(false), 3000)
    return () => clearTimeout(timer)
  }, [refetch])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-6">
      <div className="mx-auto max-w-2xl w-full">
        {/* Success Card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 md:p-12 text-center border border-gray-200 dark:border-gray-800">
          {/* Success Icon with Animation */}
          <div className="relative inline-flex items-center justify-center mb-6">
            <div className={`absolute inset-0 bg-green-500/20 rounded-full ${showConfetti ? 'animate-ping' : ''}`} />
            <div className="relative flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full">
              <CheckCircle className="h-12 w-12 text-green-600 dark:text-green-400" />
            </div>
          </div>

          {/* Success Message */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Payment Successful!
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
            Your credits have been added to your account
          </p>

          {/* Credits Info */}
          {creditsAmount && (
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6 mb-8 border border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-center gap-3 mb-2">
                <Zap className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                <span className="text-4xl font-bold text-purple-900 dark:text-purple-100">
                  +{creditsAmount}
                </span>
              </div>
              <p className="text-sm text-purple-700 dark:text-purple-300">
                Credits Added
              </p>
            </div>
          )}

          {/* Current Balance */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-8 border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Current Balance
            </p>
            <div className="flex items-center justify-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <span className="text-3xl font-bold text-gray-900 dark:text-white">
                {balanceData?.data?.total || 0}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                credits
              </span>
            </div>
          </div>

          {/* Session ID (for support) */}
          {sessionId && (
            <div className="mb-8">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Transaction ID: {sessionId}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard/credits"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-700 transition-colors"
            >
              View Credits
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-3 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Go to Dashboard
            </Link>
          </div>

          {/* Help Text */}
          <p className="mt-8 text-sm text-gray-500 dark:text-gray-400">
            A receipt has been sent to your email address.
            <br />
            Questions? <Link href="/contact" className="text-purple-600 dark:text-purple-400 hover:underline">Contact Support</Link>
          </p>
        </div>

        {/* Decorative Elements */}
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute animate-bounce"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 2}s`,
                }}
              >
                <Zap className="h-4 w-4 text-purple-500 opacity-30" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Payment Success Page
 *
 * Displayed after successful credit purchase or subscription payment
 * Shows confirmation and updated balance
 */
export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 dark:border-purple-400" />
          </div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  )
}
