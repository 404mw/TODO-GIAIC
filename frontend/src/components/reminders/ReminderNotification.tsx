'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import * as Toast from '@radix-ui/react-toast'
import type { Reminder } from '@/lib/schemas/reminder.schema'
import type { Task } from '@/lib/schemas/task.schema'
import { Button } from '@/components/ui/Button'

interface ReminderNotificationProps {
  reminder: Reminder
  task: Task
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * ReminderNotification toast component for in-app notifications
 * Per research.md Section 15 and tasks.md T090
 *
 * Features:
 * - Displays reminder with task title
 * - Click to navigate to task detail
 * - Auto-dismisses after 10 seconds
 * - Part of dual notification system (browser + in-app)
 */
export function ReminderNotification({
  reminder,
  task,
  open,
  onOpenChange,
}: ReminderNotificationProps) {
  const router = useRouter()

  // Auto-dismiss after 10 seconds
  useEffect(() => {
    if (open) {
      const timer = setTimeout(() => {
        onOpenChange(false)
      }, 10000)

      return () => clearTimeout(timer)
    }
  }, [open, onOpenChange])

  const handleViewTask = () => {
    router.push(`/dashboard/tasks/${task.id}`)
    onOpenChange(false)
  }

  return (
    <Toast.Root
      className="grid grid-cols-[auto_max-content] items-center gap-x-4 rounded-lg border border-blue-500/50 bg-gray-900/95 p-4 shadow-lg backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full"
      open={open}
      onOpenChange={onOpenChange}
    >
      {/* Icon */}
      <div className="row-span-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20">
          <svg
            className="h-6 w-6 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
        </div>
      </div>

      {/* Content */}
      <div className="col-start-2 row-start-1">
        <Toast.Title className="text-sm font-semibold text-gray-100">
          {reminder.title}
        </Toast.Title>
        <Toast.Description className="mt-1 text-sm text-gray-300">
          {task.title}
        </Toast.Description>
      </div>

      {/* Action */}
      <div className="col-start-2 row-start-2 flex gap-2">
        <Toast.Action altText="View task" asChild>
          <Button
            variant="primary"
            size="sm"
            onClick={handleViewTask}
            className="mt-2"
          >
            View Task
          </Button>
        </Toast.Action>
      </div>

      {/* Close button */}
      <Toast.Close
        className="absolute right-2 top-2 rounded-md p-1 text-gray-400 hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Close notification"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </Toast.Close>
    </Toast.Root>
  )
}

/**
 * ReminderToastProvider - Wraps app to provide toast context
 * Must be added to root layout
 */
export function ReminderToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <Toast.Provider swipeDirection="right">
      {children}
      <Toast.Viewport className="fixed bottom-0 right-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]" />
    </Toast.Provider>
  )
}
