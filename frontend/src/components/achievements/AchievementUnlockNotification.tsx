'use client'

import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAchievementNotificationStore } from '@/lib/stores/useAchievementNotificationStore'

/**
 * Achievement Unlock Notification Component
 *
 * Displays a celebratory modal when achievements are unlocked.
 * Shows:
 * - Achievement name and description
 * - Perk granted (if any)
 * - Celebration animation
 *
 * Auto-dismisses after 5 seconds or can be manually dismissed.
 */

export function AchievementUnlockNotification() {
  const { isVisible, currentAchievement, dismiss } = useAchievementNotificationStore()

  // Auto-dismiss after 5 seconds
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        dismiss()
      }, 5000)

      return () => clearTimeout(timer)
    }
  }, [isVisible, dismiss])

  // Close on Escape key
  useEffect(() => {
    if (!isVisible) return

    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        dismiss()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isVisible, dismiss])

  if (!currentAchievement) return null

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={dismiss}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.5, opacity: 0, y: 100 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 50 }}
              transition={{ type: 'spring', damping: 20, stiffness: 300 }}
              className="relative w-full max-w-md rounded-2xl border border-yellow-200 bg-white p-8 shadow-2xl dark:border-yellow-800/50 dark:bg-gray-900"
            >
              {/* Celebration Confetti Effect */}
              <div className="absolute inset-0 overflow-hidden rounded-2xl">
                {Array.from({ length: 20 }).map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ y: -20, x: Math.random() * 100 - 50, opacity: 1 }}
                    animate={{
                      y: 500,
                      x: Math.random() * 200 - 100,
                      opacity: 0,
                      rotate: Math.random() * 360,
                    }}
                    transition={{
                      duration: 2 + Math.random() * 2,
                      ease: 'easeOut',
                      delay: Math.random() * 0.5,
                    }}
                    className="absolute h-3 w-3 rounded-full"
                    style={{
                      left: `${Math.random() * 100}%`,
                      backgroundColor: ['#f59e0b', '#ef4444', '#8b5cf6', '#10b981', '#3b82f6'][
                        Math.floor(Math.random() * 5)
                      ],
                    }}
                  />
                ))}
              </div>

              {/* Close button */}
              <button
                onClick={dismiss}
                className="absolute right-4 top-4 rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
                aria-label="Close"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>

              {/* Content */}
              <div className="relative text-center">
                {/* Icon */}
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ delay: 0.2, type: 'spring', damping: 15, stiffness: 200 }}
                  className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 shadow-lg"
                >
                  <svg
                    className="h-10 w-10 text-white"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </motion.div>

                {/* Title */}
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100"
                >
                  Achievement Unlocked!
                </motion.h2>

                {/* Achievement name */}
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mb-2 text-xl font-semibold text-yellow-600 dark:text-yellow-400"
                >
                  {currentAchievement.name}
                </motion.p>

                {/* Description */}
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mb-6 text-gray-600 dark:text-gray-400"
                >
                  {currentAchievement.description}
                </motion.p>

                {/* Perk granted */}
                {currentAchievement.perk && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6, type: 'spring' }}
                    className="mx-auto inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 px-6 py-3 dark:from-purple-900/30 dark:to-pink-900/30"
                  >
                    <svg
                      className="h-5 w-5 text-purple-600 dark:text-purple-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"
                      />
                    </svg>
                    <span className="font-semibold text-purple-700 dark:text-purple-300">
                      +{currentAchievement.perk.value}{' '}
                      {currentAchievement.perk.type.replace('_', ' ')}
                    </span>
                  </motion.div>
                )}

                {/* Dismiss button */}
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
                  onClick={dismiss}
                  className="mt-6 w-full rounded-lg bg-gradient-to-r from-yellow-400 to-orange-500 px-6 py-3 font-semibold text-white shadow-lg transition-all hover:from-yellow-500 hover:to-orange-600 hover:shadow-xl"
                >
                  Awesome!
                </motion.button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
