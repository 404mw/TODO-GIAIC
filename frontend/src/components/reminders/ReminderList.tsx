'use client'

import { motion, AnimatePresence } from 'framer-motion'
import type { Reminder } from '@/lib/schemas/reminder.schema'
import type { Task, TaskDetail, ReminderInTask } from '@/lib/schemas/task.schema'
import { formatReminderOffset, calculateReminderTriggerTime } from '@/lib/utils/date'
import { Button } from '@/components/ui/Button'
import { format } from 'date-fns'

interface ReminderListProps {
  task: Task | TaskDetail
  reminders: Reminder[] | ReminderInTask[]
  onEdit?: (reminder: Reminder | ReminderInTask) => void
  onDelete: (reminderId: string) => void | Promise<void>
}

/**
 * ReminderList component for displaying and managing task reminders
 * Per tasks.md T089 - Display all reminders with edit/delete actions
 *
 * Features:
 * - Shows trigger time in human-readable format
 * - Displays delivery status
 * - Edit and delete actions for each reminder
 */
export function ReminderList({ task, reminders, onEdit, onDelete }: ReminderListProps) {
  if (reminders.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <svg
          className="mx-auto h-12 w-12 text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        <p className="mt-2">No reminders set</p>
        <p className="text-sm text-gray-500">Add a reminder to get notified before the due date</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {reminders.map((reminder) => {
          const triggerTime = calculateReminderTriggerTime(reminder, task)
          const offsetLabel = reminder.offsetMinutes ? formatReminderOffset(reminder.offsetMinutes) : 'At scheduled time'

          return (
            <motion.div
              key={reminder.id}
              layout
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="flex items-center justify-between rounded-lg border border-gray-700/50 bg-gray-800/30 p-4 backdrop-blur-sm"
            >
              <div className="flex items-start gap-3 flex-1">
                {/* Bell icon */}
                <div className="flex-shrink-0 mt-1">
                  <svg
                    className={`h-5 w-5 ${
                      reminder.fired ? 'text-gray-500' : 'text-blue-400'
                    }`}
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

                {/* Reminder details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-medium text-gray-200">
                      {offsetLabel}
                    </p>
                    {reminder.fired && (
                      <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-0.5 text-xs font-medium text-green-400 border border-green-500/20">
                        ✓ Delivered
                      </span>
                    )}
                  </div>

                  {triggerTime && (
                    <p className="mt-1 text-sm text-gray-400">
                      Will trigger at{' '}
                      <time dateTime={triggerTime.toISOString()}>
                        {format(triggerTime, 'MMM d, yyyy h:mm a')}
                      </time>
                    </p>
                  )}

                  {!triggerTime && (
                    <p className="mt-1 text-sm text-amber-400">
                      ⚠ Cannot calculate trigger time (task may be missing due date)
                    </p>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 ml-4">
                {onEdit && !reminder.fired && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(reminder)}
                    aria-label={`Edit reminder: ${offsetLabel}`}
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
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </Button>
                )}

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(reminder.id)}
                  aria-label={`Delete reminder: ${offsetLabel}`}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
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
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </Button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
