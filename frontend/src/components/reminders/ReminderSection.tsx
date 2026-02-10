'use client'

import { useState } from 'react'
import type { Task } from '@/lib/schemas/task.schema'
import type { Reminder, ReminderCreate } from '@/lib/schemas/reminder.schema'
import { ReminderForm } from './ReminderForm'
import { ReminderList } from './ReminderList'
import { Button } from '@/components/ui/Button'

interface ReminderSectionProps {
  task: Task
  reminders: Reminder[]
  onAddReminder: (reminder: ReminderCreate) => Promise<void>
  onDeleteReminder: (reminderId: string) => Promise<void>
}

/**
 * ReminderSection component for task detail page
 * Per tasks.md T097 - Integrates reminders into task UI
 *
 * Features:
 * - Shows existing reminders with delivery status
 * - Add new reminder form
 * - Delete reminder action
 * - Collapsible section
 */
export function ReminderSection({
  task,
  reminders,
  onAddReminder,
  onDeleteReminder,
}: ReminderSectionProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [showForm, setShowForm] = useState(false)

  const handleSubmit = async (reminder: ReminderCreate) => {
    await onAddReminder(reminder)
    setShowForm(false)
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400"
        >
          <svg
            className={`h-5 w-5 transition-transform ${
              isExpanded ? 'rotate-90' : ''
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
          Reminders
          {reminders && reminders.length > 0 && (
            <span className="ml-2 inline-flex items-center rounded-full bg-blue-500/10 px-2.5 py-0.5 text-sm font-medium text-blue-400 border border-blue-500/20">
              {reminders.length}
            </span>
          )}
        </button>

        {isExpanded && !showForm && task.due_date && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowForm(true)}
          >
            <svg
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Add Reminder
          </Button>
        )}
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="space-y-4">
          {/* Existing reminders */}
          {reminders && reminders.length > 0 && (
            <ReminderList
              task={task}
              reminders={reminders}
              onDelete={onDeleteReminder}
            />
          )}

          {/* Add reminder form */}
          {showForm && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                Add New Reminder
              </h4>
              <ReminderForm
                task={task}
                onSubmit={handleSubmit}
                onCancel={() => setShowForm(false)}
              />
            </div>
          )}

          {/* No due date warning */}
          {!task.due_date && (
            <div className="text-center py-6 text-gray-400">
              <svg
                className="mx-auto h-12 w-12 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <p className="mt-2 text-sm">
                This task needs a due date before you can add reminders
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Edit the task to add a due date
              </p>
            </div>
          )}

          {/* Empty state */}
          {task.due_date && (!reminders || reminders.length === 0) && !showForm && (
            <div className="text-center py-6 text-gray-400">
              <svg
                className="mx-auto h-12 w-12 text-gray-500"
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
              <p className="mt-2">No reminders set</p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowForm(true)}
                className="mt-3"
              >
                Add your first reminder
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
