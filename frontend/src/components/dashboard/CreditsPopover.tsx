'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { useCreditsStore } from '@/lib/stores/useCreditsStore'
import { CreditType } from '@/lib/api/credits'

/**
 * Credits Popover Component
 *
 * Displays detailed credit breakdown with:
 * - Total available credits
 * - Breakdown by type (daily, subscription, kickstart, purchased)
 * - Expiration information
 * - Consumption order explanation
 * - CTA to upgrade or purchase more credits
 */

interface CreditsPopoverProps {
  /** Whether the popover is open */
  isOpen: boolean
  /** Callback to close the popover */
  onClose: () => void
  /** Anchor element (the button that triggers the popover) */
  anchorEl: HTMLElement | null
}

export function CreditsPopover({ isOpen, onClose, anchorEl }: CreditsPopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null)
  const { balance, isLoading, error, fetchCredits } = useCreditsStore()
  const [position, setPosition] = useState({ top: 0, left: 0 })

  // Fetch credits when popover opens
  useEffect(() => {
    if (isOpen) {
      fetchCredits()
    }
  }, [isOpen, fetchCredits])

  // Calculate popover position based on anchor element
  useEffect(() => {
    if (isOpen && anchorEl) {
      const rect = anchorEl.getBoundingClientRect()
      const popoverWidth = 320 // Approximate width

      // Position below the button, aligned to the right
      setPosition({
        top: rect.bottom + 8,
        left: rect.right - popoverWidth,
      })
    }
  }, [isOpen, anchorEl])

  // Close on click outside
  useEffect(() => {
    if (!isOpen) return

    function handleClickOutside(event: MouseEvent) {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(event.target as Node) &&
        anchorEl &&
        !anchorEl.contains(event.target as Node)
      ) {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, onClose, anchorEl])

  // Close on escape key
  useEffect(() => {
    if (!isOpen) return

    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={popoverRef}
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ duration: 0.15 }}
          style={{
            position: 'fixed',
            top: position.top,
            left: position.left,
            zIndex: 50,
          }}
          className="w-80 rounded-lg border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
        >
          {/* Header */}
          <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                AI Credits
              </h3>
              <button
                onClick={onClose}
                className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
                aria-label="Close"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto p-4">
            {isLoading && !balance && (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
              </div>
            )}

            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}

            {balance && (
              <div className="space-y-4">
                {/* Total Credits */}
                <div className="rounded-lg bg-gradient-to-br from-blue-50 to-purple-50 p-4 dark:from-blue-950/30 dark:to-purple-950/30">
                  <div className="text-sm text-gray-600 dark:text-gray-400">Total Available</div>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                      {balance.total}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">credits</span>
                  </div>
                </div>

                {/* Credit Breakdown */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                    Breakdown
                  </h4>

                  {/* Daily Credits */}
                  <CreditRow
                    label="Daily Credits"
                    amount={balance.daily}
                    description="Expires at midnight UTC"
                    color="text-blue-600 dark:text-blue-400"
                    icon="☀️"
                  />

                  {/* Subscription Credits */}
                  <CreditRow
                    label="Subscription Credits"
                    amount={balance.subscription}
                    description="Monthly credits (carry over up to 50)"
                    color="text-purple-600 dark:text-purple-400"
                    icon="⭐"
                  />

                  {/* Kickstart Credits */}
                  <CreditRow
                    label="Kickstart Credits"
                    amount={balance.kickstart}
                    description="Welcome bonus (never expire)"
                    color="text-green-600 dark:text-green-400"
                    icon="🎁"
                  />

                  {/* Purchased Credits */}
                  <CreditRow
                    label="Purchased Credits"
                    amount={balance.purchased}
                    description="Never expire"
                    color="text-yellow-600 dark:text-yellow-400"
                    icon="💎"
                  />
                </div>

                {/* Consumption Order */}
                <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900/50">
                  <div className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    Consumption Order
                  </div>
                  <div className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                    Credits are used in this order: Daily → Subscription → Kickstart → Purchased
                  </div>
                </div>

                {/* CTA */}
                <div className="pt-2">
                  <Link
                    href="/pricing"
                    onClick={onClose}
                    className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2.5 text-sm font-medium text-white hover:from-blue-700 hover:to-purple-700 transition-all"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                    Get More Credits
                  </Link>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * Credit row component for displaying individual credit types
 */
interface CreditRowProps {
  label: string
  amount: number
  description: string
  color: string
  icon: string
}

function CreditRow({ label, amount, description, color, icon }: CreditRowProps) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <div className="text-lg">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{label}</span>
          <span className={`text-sm font-bold ${color}`}>{amount}</span>
        </div>
        <div className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{description}</div>
      </div>
    </div>
  )
}
