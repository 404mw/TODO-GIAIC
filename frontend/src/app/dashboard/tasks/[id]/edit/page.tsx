'use client'

import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useTask } from '@/lib/hooks/useTasks'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskForm } from '@/components/tasks/TaskForm'

export default function EditTaskPage({
  params,
}: {
  params: { id: string }
}) {
  const router = useRouter()
  const { data: task, isLoading, error } = useTask(params.id)

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
              The task you're trying to edit doesn't exist or has been deleted.
            </p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <Link
            href={`/tasks/${task.id}`}
            className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Task
          </Link>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h1 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Edit Task
          </h1>
          <TaskForm
            task={task}
            onSuccess={() => router.push(`/tasks/${task.id}`)}
            onCancel={() => router.push(`/tasks/${task.id}`)}
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
