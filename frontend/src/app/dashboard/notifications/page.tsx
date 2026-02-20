'use client'

import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { useNotifications } from '@/lib/hooks/useNotifications'

export default function NotificationsPage() {
  const { data, isLoading } = useNotifications()
  const notifications = data?.data ?? []

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <div className="mx-auto max-w-2xl px-4 py-8">
          <h1 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Notifications
          </h1>
          <div
            data-testid="notifications-loading"
            className="animate-pulse space-y-4"
            aria-label="Loading notifications"
            role="status"
          >
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-16 rounded-lg bg-gray-200 dark:bg-gray-800"
              />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-2xl px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Notifications
          </h1>
        </div>

        {/* Content */}
        {notifications.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-gray-900">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <p className="mt-4 text-gray-500 dark:text-gray-400">No notifications yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white dark:divide-gray-800 dark:border-gray-800 dark:bg-gray-900">
            {[...notifications].reverse().map((notification) => (
              <div
                key={notification.id}
                className={`flex gap-4 px-4 py-4 ${
                  !notification.read
                    ? 'bg-blue-50 dark:bg-blue-950/20'
                    : ''
                }`}
              >
                <div className="flex-1 min-w-0">
                  {notification.task_id ? (
                    <Link href={`/dashboard/tasks/${notification.task_id}`} className="block">
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                        {notification.message}
                      </p>
                    </Link>
                  ) : (
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                        {notification.message}
                      </p>
                    </div>
                  )}
                  <p className="mt-1 text-xs text-gray-500">
                    {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                  </p>
                </div>
                {!notification.read && (
                  <div className="mt-2 h-2 w-2 shrink-0 rounded-full bg-blue-500" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
