/**
 * Service Worker utility functions for browser support checking
 */

/**
 * Check if the browser supports Service Workers and Notifications
 */
export function checkServiceWorkerSupport(): {
  serviceWorker: boolean
  notifications: boolean
  pushManager: boolean
} {
  if (typeof window === 'undefined') {
    return {
      serviceWorker: false,
      notifications: false,
      pushManager: false,
    }
  }

  const serviceWorker = 'serviceWorker' in navigator
  const notifications = 'Notification' in window
  const pushManager = 'PushManager' in window

  return {
    serviceWorker,
    notifications,
    pushManager,
  }
}

/**
 * Show a warning message for unsupported browsers
 */
export function showUnsupportedBrowserWarning(): string {
  const support = checkServiceWorkerSupport()

  if (!support.serviceWorker) {
    return 'Your browser does not support Service Workers. Some features may not work correctly.'
  }

  if (!support.notifications) {
    return 'Your browser does not support notifications. You will not receive reminder alerts.'
  }

  if (!support.pushManager) {
    return 'Your browser does not support push notifications. Background reminders may not work.'
  }

  return ''
}
