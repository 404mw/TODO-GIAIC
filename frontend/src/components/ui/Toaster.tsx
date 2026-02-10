'use client'

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
 */
export function Toaster() {
  const notifications = useNotificationStore((state) => state.notifications)
  const removeNotification = useNotificationStore((state) => state.removeNotification)

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
