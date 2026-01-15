'use client'

import { useState } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskList } from '@/components/tasks/TaskList'
import { useTasks } from '@/lib/hooks/useTasks'
import { useNewTaskModalStore } from '@/lib/stores/useNewTaskModalStore'
import { Button } from '@/components/ui/Button'
import type { Task } from '@/lib/schemas/task.schema'

type FilterState = 'all' | 'active' | 'high' | 'today'
type SortState = 'priority' | 'dueDate' | 'created' | 'title'
type SortDirection = 'asc' | 'desc'

/**
 * All Tasks page
 *
 * Displays all tasks with filtering and sorting options.
 * Features:
 * - Filter by status (all, active)
 * - Filter by priority (high priority)
 * - Filter by due date (due today)
 * - Sort by priority, due date, created date, or title
 * - Toggle sort direction (ascending/descending)
 * - Pending completions are handled by the global PendingCompletionsBar
 */

export default function TasksPage() {
  const [filter, setFilter] = useState<FilterState>('all')
  const [sort, setSort] = useState<SortState>('priority')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const openNewTaskModal = useNewTaskModalStore((state) => state.open)

  const {
    data: tasks = [],
    isLoading,
    error,
  } = useTasks({ hidden: false })

  // Apply filters - only show non-completed tasks (completed tasks have their own page)
  const filteredTasks = tasks.filter((task: Task) => {
    // Always exclude completed tasks from All Tasks page
    if (task.completed) return false

    switch (filter) {
      case 'active':
        return !task.completed
      case 'high':
        return task.priority === 'high'
      case 'today': {
        const today = new Date().toISOString().split('T')[0]
        return task.dueDate?.startsWith(today)
      }
      default:
        return true
    }
  })

  // Apply sorting with direction
  const sortedTasks = [...filteredTasks].sort((a: Task, b: Task) => {
    let comparison = 0

    switch (sort) {
      case 'priority': {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        const aPriority = priorityOrder[a.priority || 'medium']
        const bPriority = priorityOrder[b.priority || 'medium']
        if (aPriority !== bPriority) {
          comparison = aPriority - bPriority
        } else {
          // Secondary sort by due date
          if (a.dueDate && b.dueDate) comparison = a.dueDate.localeCompare(b.dueDate)
          else if (a.dueDate) comparison = -1
          else if (b.dueDate) comparison = 1
        }
        break
      }
      case 'dueDate': {
        if (a.dueDate && b.dueDate) comparison = a.dueDate.localeCompare(b.dueDate)
        else if (a.dueDate) comparison = -1
        else if (b.dueDate) comparison = 1
        break
      }
      case 'created':
        comparison = a.createdAt.localeCompare(b.createdAt)
        break
      case 'title':
        comparison = a.title.localeCompare(b.title)
        break
    }

    return sortDirection === 'desc' ? -comparison : comparison
  })

  const filterButtons: { value: FilterState; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'active', label: 'Active' },
    { value: 'high', label: 'High Priority' },
    { value: 'today', label: 'Due Today' },
  ]

  const sortOptions: { value: SortState; label: string }[] = [
    { value: 'priority', label: 'Priority' },
    { value: 'dueDate', label: 'Due Date' },
    { value: 'created', label: 'Created' },
    { value: 'title', label: 'Title' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              All Tasks
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
              {filter !== 'all' && ` (filtered)`}
            </p>
          </div>
          <Button onClick={openNewTaskModal}>
            <svg
              className="mr-2 h-4 w-4"
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
            New Task
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Filter buttons */}
          <div className="flex flex-wrap gap-2">
            {filterButtons.map((btn) => (
              <button
                key={btn.value}
                onClick={() => setFilter(btn.value)}
                className={[
                  'rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors',
                  filter === btn.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-900/20 dark:text-blue-300'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-gray-600',
                ].join(' ')}
              >
                {btn.label}
              </button>
            ))}
          </div>

          {/* Sort dropdown and direction */}
          <div className="flex items-center gap-2 ml-auto">
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
        </div>

        {/* Task List */}
        <TaskList
          tasks={sortedTasks}
          isLoading={isLoading}
          error={error}
          emptyMessage={
            filter === 'all'
              ? "No tasks yet. Create your first task to get started!"
              : `No ${filter} tasks found.`
          }
        />
      </div>
    </DashboardLayout>
  )
}
