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
  const { data: task, isLoading, error } = useTask(id)

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
    return (
      <DashboardLayout>
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Task not found
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              The task you're looking for doesn't exist or has been deleted.
            </p>
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
