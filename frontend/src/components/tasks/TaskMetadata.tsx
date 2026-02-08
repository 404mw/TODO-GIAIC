'use client'

import { format } from 'date-fns'
import type { Task, TaskDetail } from '@/lib/schemas/task.schema'

interface TaskMetadataProps {
  task: Task | TaskDetail
}

export function TaskMetadata({ task }: TaskMetadataProps) {
  const priorityConfig = {
    low: { label: 'Low', color: 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800' },
    medium: { label: 'Medium', color: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900' },
    high: { label: 'High', color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900' },
  }

  const priorityStyle = task.priority ? priorityConfig[task.priority] : null

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {/* Priority */}
      {task.priority && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Priority
          </div>
          <div className="mt-1">
            <span
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${priorityStyle?.color}`}
            >
              {priorityStyle?.label}
            </span>
          </div>
        </div>
      )}

      {/* Due Date */}
      {task.dueDate && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Due Date
          </div>
          <div className="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {format(new Date(task.dueDate), 'PPP')}
          </div>
        </div>
      )}

      {/* Estimated Duration */}
      {task.estimatedDuration && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Estimated Time
          </div>
          <div className="mt-1 text-sm text-gray-900 dark:text-gray-100">
            {task.estimatedDuration} minutes
          </div>
        </div>
      )}

      {/* Tags */}
      {task.tags && task.tags.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900 sm:col-span-2 lg:col-span-3">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Tags
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recurring */}
      {task.recurrence?.enabled && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900 sm:col-span-2 lg:col-span-3">
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Recurrence
          </div>
          <div className="mt-1 flex items-center gap-2 text-sm text-gray-900 dark:text-gray-100">
            <svg
              className="h-4 w-4 text-blue-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <span>{task.recurrence.humanReadable || task.recurrence.rule}</span>
          </div>
        </div>
      )}

      {/* Created/Updated */}
      <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900 sm:col-span-2 lg:col-span-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Created
            </div>
            <div className="mt-1 text-sm text-gray-900 dark:text-gray-100">
              {format(new Date(task.createdAt), 'PPpp')}
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
              Last Updated
            </div>
            <div className="mt-1 text-sm text-gray-900 dark:text-gray-100">
              {format(new Date(task.updatedAt), 'PPpp')}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
