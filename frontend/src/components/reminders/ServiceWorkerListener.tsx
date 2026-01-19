'use client'

import { useEffect } from 'react'
import { checkServiceWorkerSupport, showUnsupportedBrowserWarning } from '@/lib/utils/service-worker'
import { useToast } from '@/lib/hooks/useToast'
import { playNotificationSound } from '@/lib/config/notification-sounds'

/**
 * ServiceWorkerListener - Manages Service Worker registration and reminder polling
 * Per PHASE5_INTEGRATION_GUIDE.md Step 4
 *
 * Features:
 * - Registers Service Worker for background notifications
 * - Starts reminder polling (60-second interval)
 * - Listens for REMINDER_DUE messages from Service Worker
 * - Shows graceful fallback warning for unsupported browsers (T099)
 * - Plays notification sound when browser notification shown (T101)
 */
export function ServiceWorkerListener() {
  const { toast } = useToast()
  useEffect(() => {
    // T099: Check Service Worker support before attempting registration
    if (!checkServiceWorkerSupport()) {
      console.warn('[App] Service Worker not supported in this browser')
      const warning = showUnsupportedBrowserWarning()
      toast(warning)
      return
    }

    if ('serviceWorker' in navigator) {
      // Register Service Worker
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          console.log('[App] Service Worker registered:', registration)

          // Start reminder polling
          if (registration.active) {
            registration.active.postMessage({ type: 'START_REMINDER_POLLING' })
          }

          // Handle state changes (installing -> active)
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'activated') {
                  console.log('[App] New Service Worker activated')
                  newWorker.postMessage({ type: 'START_REMINDER_POLLING' })
                }
              })
            }
          })
        })
        .catch((error) => {
          console.error('[App] Service Worker registration failed:', error)
          // T099: Show warning on registration failure
          const warning = showUnsupportedBrowserWarning()
          toast(warning)
        })

      // Listen for reminder notifications from Service Worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'REMINDER_DUE') {
          const { reminder, task, fallbackToast } = event.data

          console.log('[App] Reminder notification received:', {
            reminder: reminder.title,
            task: task.title,
            fallbackToast,
          })

          // Note: The toast will be shown automatically via the ReminderToastProvider
          // The ReminderToastProvider listens to the same message event and displays the toast

          // T101: Play notification sound when browser notification shown
          if (!fallbackToast) {
            // Browser notification was shown, play sound for additional feedback
            playNotificationSound('default')
          }
        }
      })
    }

    // Cleanup on unmount
    return () => {
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'STOP_REMINDER_POLLING',
        })
      }
    }
  }, [])

  return null // This component doesn't render anything
}
