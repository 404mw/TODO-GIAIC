'use client'

import { useMemo } from 'react'
import type { Task } from '@/lib/schemas/task.schema'
import { TaskCard } from './TaskCard'

/**
 * Task list component
 *
 * Displays a list of tasks with:
 * - Empty state when no tasks
 * - Loading state
 * - Error state
 * - Priority sorting (high > medium > low) - T072
 * - Hidden task filtering - T072
 */

interface TaskListProps {
  tasks?: Task[]
  isLoading?: boolean
  error?: Error | null
  emptyMessage?: string
  showHidden?: boolean // T072: Support viewing hidden tasks
}

export function TaskList({
  tasks = [],
  isLoading = false,
  error = null,
  emptyMessage = 'No tasks found',
  showHidden = false, // T072: Default to hiding hidden tasks (FR-006)
}: TaskListProps) {
  // T072: Filter and sort tasks
  const displayTasks = useMemo(() => {
    if (!tasks || tasks.length === 0) return []

    // Filter hidden tasks based on showHidden prop (FR-005, FR-006)
    let filteredTasks = showHidden
      ? tasks.filter((task) => task.hidden === true)
      : tasks.filter((task) => task.hidden !== true)

    // Sort by priority: high > medium > low (T072)
    const priorityOrder: Record<string, number> = {
      high: 3,
      medium: 2,
      low: 1,
    }

    return filteredTasks.sort((a, b) => {
      const priorityA = priorityOrder[a.priority] || 0
      const priorityB = priorityOrder[b.priority] || 0
      return priorityB - priorityA // Descending order (high first)
    })
  }, [tasks, showHidden])

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-32 animate-pulse rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-800 dark:bg-gray-900"
          />
        ))}
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center dark:border-red-900 dark:bg-red-950">
        <svg
          className="mx-auto h-12 w-12 text-red-600 dark:text-red-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-red-900 dark:text-red-100">
          Failed to load tasks
        </h3>
        <p className="mt-2 text-sm text-red-700 dark:text-red-300">{error.message}</p>
      </div>
    )
  }

  // Empty state
  if (displayTasks.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center dark:border-gray-700 dark:bg-gray-900">
        <svg
          className="mx-auto h-16 w-16 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
          {emptyMessage}
        </h3>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {showHidden
            ? 'No hidden tasks. Tasks you hide will appear here.'
            : 'Get started by creating your first task'}
        </p>
      </div>
    )
  }

  // Task list with priority sorting
  return (
    <div className="space-y-3">
      {displayTasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  )
}
