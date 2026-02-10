'use client'

import { use } from 'react'
import { useTask } from '@/lib/hooks/useTasks'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskDetailView } from '@/components/tasks/TaskDetailView'

export default function TaskDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const { data: taskResponse, isLoading, error } = useTask(id)

  // Unwrap API response
  const task = taskResponse?.data

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent mx-auto"></div>
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              Loading task...
            </p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !task) {
    // Log error for debugging
    if (error) {
      console.error('[TaskDetail] Failed to load task:', {
        taskId: id,
        error,
        message: error instanceof Error ? error.message : 'Unknown error',
      })
    }

    return (
      <DashboardLayout>
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="text-center max-w-lg mx-auto px-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Task not found
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              The task you're looking for doesn't exist or has been deleted.
            </p>
            {process.env.NODE_ENV === 'development' && error && (
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                  Error Details (dev only)
                </summary>
                <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto max-h-64 text-red-600 dark:text-red-400">
                  {JSON.stringify(error, null, 2)}
                </pre>
              </details>
            )}
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <TaskDetailView task={task} />
    </DashboardLayout>
  )
}
