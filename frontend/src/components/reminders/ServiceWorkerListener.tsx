'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { checkServiceWorkerSupport, showUnsupportedBrowserWarning } from '@/lib/utils/service-worker'
import { useToast } from '@/lib/hooks/useToast'
import { playNotificationSound } from '@/lib/config/notification-sounds'
import { useAuth } from '@/lib/hooks/useAuth'

/**
 * ServiceWorkerListener - Manages Service Worker registration and reminder polling
 * Per PHASE5_INTEGRATION_GUIDE.md Step 4
 *
 * Features:
 * - Registers Service Worker for background notifications
 * - Starts reminder polling (60-second interval) only on protected routes when authenticated
 * - Listens for REMINDER_DUE messages from Service Worker
 * - Shows graceful fallback warning for unsupported browsers (T099)
 * - Plays notification sound when browser notification shown (T101)
 */
export function ServiceWorkerListener() {
  const { toast } = useToast()
  const { isAuthenticated } = useAuth()
  const pathname = usePathname()

  // Only register and poll on protected routes when user is authenticated
  const isProtectedRoute = pathname?.startsWith('/dashboard') || pathname?.startsWith('/app')
  const shouldEnablePolling = isAuthenticated && isProtectedRoute

  useEffect(() => {
    // T099: Check Service Worker support before attempting registration
    if (!checkServiceWorkerSupport()) {
      console.warn('[App] Service Worker not supported in this browser')
      const warning = showUnsupportedBrowserWarning()
      toast({ title: 'Browser Compatibility', message: warning, type: 'warning' })
      return
    }

    // Skip registration on public pages to avoid unnecessary API requests
    if (!shouldEnablePolling) {
      console.log('[App] Skipping Service Worker polling on public page or unauthenticated')
      return
    }

    if ('serviceWorker' in navigator) {
      // Register Service Worker
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          console.log('[App] Service Worker registered:', registration)

          // Configure API URL from environment variable
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

          // Start reminder polling
          if (registration.active) {
            // Send API URL configuration first
            registration.active.postMessage({
              type: 'SET_API_URL',
              url: apiUrl
            })
            // Then start polling
            registration.active.postMessage({ type: 'START_REMINDER_POLLING' })
          }

          // Handle state changes (installing -> active)
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'activated') {
                  console.log('[App] New Service Worker activated')
                  // Configure API URL for new worker
                  newWorker.postMessage({
                    type: 'SET_API_URL',
                    url: apiUrl
                  })
                  // Then start polling
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
          toast({ title: 'Service Worker Error', message: warning, type: 'error' })
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

    // Cleanup on unmount or when leaving protected routes
    return () => {
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'STOP_REMINDER_POLLING',
        })
      }
    }
  }, [shouldEnablePolling, toast])

  return null // This component doesn't render anything
}
