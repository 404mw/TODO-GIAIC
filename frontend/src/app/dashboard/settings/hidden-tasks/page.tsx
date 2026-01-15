'use client'

import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useTasks, useUpdateTask, useDeleteTask } from '@/lib/hooks/useTasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import type { Task } from '@/lib/schemas/task.schema'

/**
 * Hidden Tasks management page (FR-007)
 *
 * Displays all hidden tasks with options to:
 * - Unhide: Restore task to main views
 * - Delete: Permanently remove task
 */

export default function HiddenTasksPage() {
  const { toast } = useToast()
  const { data: tasks = [], isLoading, error } = useTasks({ hidden: true })
  const updateTask = useUpdateTask()
  const deleteTask = useDeleteTask()

  const handleUnhide = async (task: Task) => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        input: { hidden: false },
      })
      toast({
        title: 'Task restored',
        description: `"${task.title}" is now visible in your task list`,
        variant: 'success',
      })
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to restore task',
        variant: 'error',
      })
    }
  }

  const handleDelete = async (task: Task) => {
    const confirmed = confirm(
      `Are you sure you want to permanently delete "${task.title}"? This action cannot be undone.`
    )
    if (!confirmed) return

    try {
      await deleteTask.mutateAsync(task.id)
      toast({
        title: 'Task deleted',
        description: 'The task has been permanently deleted',
        variant: 'success',
      })
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to delete task',
        variant: 'error',
      })
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link
            href="/settings"
            className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Hidden Tasks
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage tasks you've hidden from your main views
            </p>
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
          </div>
        ) : error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200">
            <p className="font-medium">Failed to load hidden tasks</p>
            <p className="text-sm">Please try refreshing the page.</p>
          </div>
        ) : tasks.length === 0 ? (
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
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
            <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              No hidden tasks
            </h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Tasks you hide will appear here for you to restore or delete.
            </p>
            <Link href="/tasks" className="mt-4 inline-block">
              <Button variant="outline">View All Tasks</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task: Task) => (
              <div
                key={task.id}
                className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
              >
                <div className="min-w-0 flex-1">
                  <h3 className="truncate font-medium text-gray-900 dark:text-gray-100">
                    {task.title}
                  </h3>
                  <div className="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                    {/* Priority badge */}
                    <span
                      className={[
                        'rounded px-2 py-0.5 text-xs font-medium',
                        task.priority === 'high'
                          ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                          : task.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                          : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
                      ].join(' ')}
                    >
                      {task.priority || 'medium'}
                    </span>
                    {/* Status */}
                    {task.completed && (
                      <span className="text-green-600 dark:text-green-400">Completed</span>
                    )}
                    {/* Due date */}
                    {task.dueDate && (
                      <span>
                        Due: {new Date(task.dueDate).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="ml-4 flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleUnhide(task)}
                    disabled={updateTask.isPending}
                  >
                    <svg
                      className="mr-1.5 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                      />
                    </svg>
                    Restore
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(task)}
                    disabled={deleteTask.isPending}
                  >
                    <svg
                      className="mr-1.5 h-4 w-4"
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
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
