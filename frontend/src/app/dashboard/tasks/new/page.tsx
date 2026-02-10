'use client'

import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskForm } from '@/components/tasks/TaskForm'
import Link from 'next/link'

export default function NewTaskPage() {
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl py-8">
        <div className="mb-6">
          <Link
            href="/dashboard/tasks"
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
            Back to Tasks
          </Link>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h1 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Create New Task
          </h1>
          <TaskForm />
        </div>
      </div>
    </DashboardLayout>
  )
}
