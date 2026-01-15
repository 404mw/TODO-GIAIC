'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'

/**
 * NotificationPermissionPrompt - Requests browser notification permission on first visit
 * Per PHASE5_INTEGRATION_GUIDE.md Step 5 (T098)
 *
 * Features:
 * - Shows prompt banner on first app visit if permission not yet decided
 * - Remembers user's choice in localStorage
 * - Dismissable if user wants to decide later
 * - Only renders if browser supports notifications
 */
export function NotificationPermissionPrompt() {
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setPermission(Notification.permission)

      // Show prompt on first visit if permission not yet decided
      const hasSeenPrompt = localStorage.getItem('notification-prompt-seen')
      if (Notification.permission === 'default' && !hasSeenPrompt) {
        setShowPrompt(true)
      }
    }
  }, [])

  const requestPermission = async () => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      const result = await Notification.requestPermission()
      setPermission(result)
      localStorage.setItem('notification-prompt-seen', 'true')
      setShowPrompt(false)
    }
  }

  const dismissPrompt = () => {
    localStorage.setItem('notification-prompt-seen', 'true')
    setShowPrompt(false)
  }

  // Don't render if browser doesn't support notifications
  if (typeof window === 'undefined' || !('Notification' in window)) {
    return null
  }

  // Don't render if already granted or denied, or user dismissed prompt
  if (!showPrompt || permission !== 'default') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md rounded-lg border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-3 flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-blue-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
        </div>

        <div className="flex-1">
          <h3 className="mb-1 text-sm font-semibold text-gray-900 dark:text-gray-100">
            Enable Task Reminders
          </h3>
          <p className="mb-3 text-sm text-gray-600 dark:text-gray-400">
            Allow notifications to receive reminders for your tasks with due dates. You can
            always change this later in your browser settings.
          </p>

          <div className="flex items-center gap-2">
            <Button size="sm" onClick={requestPermission}>
              Enable Notifications
            </Button>
            <Button variant="outline" size="sm" onClick={dismissPrompt}>
              Not Now
            </Button>
          </div>
        </div>

        <button
          onClick={dismissPrompt}
          className="flex-shrink-0 text-gray-400 transition-colors hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="Close"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
  )
}
