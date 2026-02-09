'use client'

import { useState } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskList } from '@/components/tasks/TaskList'
import { useTasks } from '@/lib/hooks/useTasks'
import type { Task } from '@/lib/schemas/task.schema'

type SortState = 'completedAt' | 'priority' | 'title'
type SortDirection = 'asc' | 'desc'

/**
 * Completed Tasks page
 *
 * Displays all completed tasks with sorting options.
 * Features:
 * - Sort by completion date, priority, or title
 * - Toggle sort direction (ascending/descending)
 */

export default function CompletedTasksPage() {
  const [sort, setSort] = useState<SortState>('completedAt')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const {
    data: tasksResponse,
    isLoading,
    error,
  } = useTasks({ completed: true })

  // Unwrap API response
  const tasks = tasksResponse?.data || []

  // Filter only completed tasks
  const completedTasks = tasks.filter((task: Task) => task.completed)

  // Apply sorting with direction
  const sortedTasks = [...completedTasks].sort((a: Task, b: Task) => {
    let comparison = 0

    switch (sort) {
      case 'completedAt': {
        // Sort by completed_at if available, otherwise by updated_at
        const aDate = a.completed_at || a.updated_at
        const bDate = b.completed_at || b.updated_at
        comparison = aDate.localeCompare(bDate)
        break
      }
      case 'priority': {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        const aPriority = priorityOrder[a.priority || 'medium']
        const bPriority = priorityOrder[b.priority || 'medium']
        comparison = aPriority - bPriority
        break
      }
      case 'title':
        comparison = a.title.localeCompare(b.title)
        break
    }

    return sortDirection === 'desc' ? -comparison : comparison
  })

  const sortOptions: { value: SortState; label: string }[] = [
    { value: 'completedAt', label: 'Completed Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'title', label: 'Title' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Completed Tasks
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {completedTasks.length} {completedTasks.length === 1 ? 'task' : 'tasks'} completed
            </p>
          </div>
        </div>

        {/* Sort controls */}
        <div className="flex items-center gap-2">
          <label htmlFor="sort" className="text-sm text-gray-600 dark:text-gray-400">
            Sort by:
          </label>
          <select
            id="sort"
            value={sort}
            onChange={(e) => setSort(e.target.value as SortState)}
            className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
            className="rounded-lg border border-gray-200 bg-white p-1.5 text-gray-600 hover:border-gray-300 hover:text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-100 transition-colors"
            aria-label={sortDirection === 'asc' ? 'Sort descending' : 'Sort ascending'}
            title={sortDirection === 'asc' ? 'Sort descending' : 'Sort ascending'}
          >
            {sortDirection === 'asc' ? (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4 4m0 0l4-4m-4 4V4" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
              </svg>
            )}
          </button>
        </div>

        {/* Task List */}
        <TaskList
          tasks={sortedTasks}
          isLoading={isLoading}
          error={error}
          emptyMessage="No completed tasks yet. Complete some tasks to see them here!"
        />
      </div>
    </DashboardLayout>
  )
}
