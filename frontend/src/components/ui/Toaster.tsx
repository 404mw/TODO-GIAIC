'use client'

import { useState, useEffect } from 'react'
import { useNotificationStore } from '@/lib/stores/notification.store'
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui/Toast'

/**
 * Toaster component for rendering toast notifications
 *
 * Place this component in the root layout to enable
 * toast notifications throughout the application.
 *
 * Note: Toast popups are hidden on mobile (<1024px).
 * Notifications are still added to the notification center.
 */
export function Toaster() {
  const notifications = useNotificationStore((state) => state.notifications)
  const removeNotification = useNotificationStore((state) => state.removeNotification)
  const [isMobile, setIsMobile] = useState(false)

  // Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024)
    }

    // Initial check
    checkMobile()

    // Listen for resize
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Don't show toast popups on mobile - notifications still go to notification center
  if (isMobile) {
    return null
  }

  return (
    <ToastProvider>
      {notifications.map(function (notification) {
        return (
          <Toast key={notification.id} variant={notification.type}>
            <div className="grid gap-1">
              {notification.title && <ToastTitle>{notification.title}</ToastTitle>}
              {notification.message && <ToastDescription>{notification.message}</ToastDescription>}
            </div>
            <ToastClose onClick={() => removeNotification(notification.id)} />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
