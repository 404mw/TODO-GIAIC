'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { CheckCircle, Sparkles, Zap, TrendingUp, Mic, Repeat, ArrowRight } from 'lucide-react'
import { useSubscription } from '@/lib/hooks/useSubscription'

/**
 * Subscription Success Content Component
 * Handles search params and displays success message
 */
function SubscriptionSuccessContent() {
  const searchParams = useSearchParams()
  const { data: subscriptionData, refetch } = useSubscription()
  const [showCelebration, setShowCelebration] = useState(true)

  const sessionId = searchParams.get('session_id')

  useEffect(() => {
    // Refetch subscription to show updated status
    refetch()

    // Hide celebration after 4 seconds
    const timer = setTimeout(() => setShowCelebration(false), 4000)
    return () => clearTimeout(timer)
  }, [refetch])

  const proFeatures = [
    {
      icon: <TrendingUp className="h-5 w-5" />,
      title: '200 Active Tasks',
      description: '4x more tasks to manage your projects',
    },
    {
      icon: <Sparkles className="h-5 w-5" />,
      title: 'AI Sub-task Generation',
      description: 'Automatically break down complex tasks',
    },
    {
      icon: <Zap className="h-5 w-5" />,
      title: '100 Monthly AI Credits',
      description: 'Plus 10 daily credits for AI features',
    },
    {
      icon: <Mic className="h-5 w-5" />,
      title: 'Voice Notes',
      description: 'Transcribe your voice notes with AI',
    },
    {
      icon: <Repeat className="h-5 w-5" />,
      title: 'Recurring Tasks',
      description: 'Set up tasks that repeat automatically',
    },
    {
      icon: <CheckCircle className="h-5 w-5" />,
      title: 'Priority Support',
      description: 'Get help faster when you need it',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-6">
      <div className="mx-auto max-w-4xl w-full">
        {/* Success Card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 md:p-12 border border-gray-200 dark:border-gray-800">
          {/* Success Header */}
          <div className="text-center mb-8">
            {/* Success Icon with Animation */}
            <div className="relative inline-flex items-center justify-center mb-6">
              <div className={`absolute inset-0 bg-purple-500/20 rounded-full ${showCelebration ? 'animate-ping' : ''}`} />
              <div className="relative flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-full">
                <CheckCircle className="h-12 w-12 text-purple-600 dark:text-purple-400" />
              </div>
            </div>

            {/* Welcome Message */}
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Welcome to Pro! 🎉
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
              Your subscription is now active
            </p>
            {subscriptionData?.data?.current_period_end && (
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Renews on {new Date(subscriptionData.data.current_period_end).toLocaleDateString()}
              </p>
            )}
          </div>

          {/* Pro Badge */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6 mb-8 border border-purple-200 dark:border-purple-800">
            <div className="flex items-center justify-center gap-3">
              <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              <span className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                You're now a Pro member
              </span>
              <Sparkles className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>

          {/* Unlocked Features */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 text-center">
              What You've Unlocked
            </h2>
            <div className="grid sm:grid-cols-2 gap-4">
              {proFeatures.map((feature, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex-shrink-0">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Session ID (for support) */}
          {sessionId && (
            <div className="mb-8 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Transaction ID: {sessionId}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 px-8 py-3 text-sm font-semibold text-white hover:from-purple-700 hover:to-blue-700 transition-all"
            >
              Start Using Pro Features
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/dashboard/settings"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-8 py-3 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Manage Subscription
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              A receipt has been sent to your email address.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Questions? <Link href="/contact" className="text-purple-600 dark:text-purple-400 hover:underline">Contact our support team</Link>
            </p>
          </div>
        </div>

        {/* Decorative Sparkles */}
        {showCelebration && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {[...Array(30)].map((_, i) => (
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
                <Sparkles className="h-4 w-4 text-purple-500 opacity-40" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Subscription Success Page
 *
 * Displayed after successful Pro subscription payment
 * Shows welcome message and unlocked features
 */
export default function SubscriptionSuccessPage() {
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
      <SubscriptionSuccessContent />
    </Suspense>
  )
}
