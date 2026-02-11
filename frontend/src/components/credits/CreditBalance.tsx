/**
 * CreditBalance Component
 * Phase 5 - Credit Display
 *
 * Displays user's AI credit balance with breakdown:
 * - Total credits available
 * - Daily credits (resets daily)
 * - Subscription credits (Pro tier)
 * - Purchased credits (one-time purchases)
 * - Kickstart credits (initial bonus)
 * - Next daily reset time
 */

'use client'

import { useState, useEffect } from 'react'
import { creditsService } from '@/lib/services/credits.service'
import type { CreditBalance as CreditBalanceType } from '@/lib/schemas/credit.schema'
import { ApiError } from '@/lib/api/client'
import { formatDistanceToNow } from 'date-fns'

interface CreditBalanceProps {
  /** Show detailed breakdown */
  detailed?: boolean
  /** Compact mode for headers/navbars */
  compact?: boolean
  /** Auto-refresh interval in ms (default: 60000 = 1 minute) */
  refreshInterval?: number
}

export function CreditBalance({
  detailed = false,
  compact = false,
  refreshInterval = 60000,
}: CreditBalanceProps) {
  const [balance, setBalance] = useState<CreditBalanceType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function fetchBalance() {
    try {
      const response = await creditsService.getBalance()
      setBalance(response.data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch credit balance:', err)
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to load credit balance')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBalance()

    // Auto-refresh balance
    const interval = setInterval(fetchBalance, refreshInterval)
    return () => clearInterval(interval)
  }, [refreshInterval])

  if (loading) {
    return (
      <div className={compact ? 'text-sm' : 'p-4'}>
        <div className="animate-pulse flex items-center gap-2">
          <div className="h-4 w-4 bg-gray-300 dark:bg-gray-700 rounded-full" />
          <div className="h-4 w-16 bg-gray-300 dark:bg-gray-700 rounded" />
        </div>
      </div>
    )
  }

  if (error || !balance) {
    return (
      <div className={compact ? 'text-sm text-red-600' : 'p-4'}>
        <span className="text-red-600 dark:text-red-400">{error || 'Error loading credits'}</span>
      </div>
    )
  }

  const { total, daily, subscription, purchased, kickstart } = balance

  // Compact mode for headers/navbars
  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <svg
          className="h-4 w-4 text-purple-600 dark:text-purple-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        <span className="font-semibold text-gray-900 dark:text-gray-100">{total}</span>
        <span className="text-xs text-gray-500 dark:text-gray-400">credits</span>
        {subscription > 0 && (
          <span className="ml-1 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
            Pro
          </span>
        )}
      </div>
    )
  }

  // Detailed breakdown mode
  if (detailed) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Credit Balance</h3>
          {subscription > 0 && (
            <span className="rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
              Pro Tier
            </span>
          )}
        </div>

        {/* Total */}
        <div className="mb-4 rounded-lg bg-linear-to-r from-purple-50 to-blue-50 p-4 dark:from-purple-950/30 dark:to-blue-950/30">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Available</span>
            <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">{total}</span>
          </div>
        </div>

        {/* Breakdown */}
        <div className="space-y-3">
          {/* Daily credits */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Daily Credits</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Resets daily at midnight</div>
            </div>
            <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">{daily}</span>
          </div>

          {/* Subscription credits (Pro only) */}
          {subscription > 0 && (
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Subscription Credits</div>
              <span className="text-lg font-semibold text-purple-600 dark:text-purple-400">{subscription}</span>
            </div>
          )}

          {/* Purchased credits */}
          {purchased > 0 && (
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Purchased Credits</div>
              <span className="text-lg font-semibold text-blue-600 dark:text-blue-400">{purchased}</span>
            </div>
          )}

          {/* Kickstart bonus */}
          {kickstart > 0 && (
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Kickstart Bonus</div>
              <span className="text-lg font-semibold text-green-600 dark:text-green-400">{kickstart}</span>
            </div>
          )}
        </div>

        {/* Low credit warning */}
        {total < 10 && (
          <div className="mt-4 rounded-md bg-yellow-50 p-3 dark:bg-yellow-900/20">
            <div className="flex gap-2">
              <svg
                className="h-5 w-5 shrink-0 text-yellow-600 dark:text-yellow-400"
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
              <div>
                <p className="text-sm font-medium text-yellow-700 dark:text-yellow-300">Low credit balance</p>
                <p className="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
                  {subscription === 0
                    ? 'Upgrade to Pro for more daily credits and bonus features.'
                    : 'Consider purchasing additional credits to continue using AI features.'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Default mode - simple display
  return (
    <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
      <svg
        className="h-8 w-8 text-purple-600 dark:text-purple-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
      <div>
        <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{total}</div>
        <div className="text-sm text-gray-500 dark:text-gray-400">AI Credits Available</div>
      </div>
      {subscription > 0 && (
        <span className="ml-auto rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
          Pro
        </span>
      )}
    </div>
  )
}
