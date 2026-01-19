'use client'

import type { Task } from '@/lib/schemas/task.schema'

interface TaskSelectorProps {
  tasks: Task[]
  selectedTaskId: string | null
  onSelect: (taskId: string) => void
}

export function TaskSelector({ tasks, selectedTaskId, onSelect }: TaskSelectorProps) {
  // Filter to incomplete tasks
  const incompleteTasks = tasks.filter((t) => !t.completed && !t.hidden)

  if (incompleteTasks.length === 0) {
    return (
      <div className="py-8 text-center text-gray-500 dark:text-gray-400">
        <p>No tasks available.</p>
        <p className="mt-2 text-sm">Create a task first to use Focus Mode.</p>
      </div>
    )
  }

  const priorityOrder = { high: 0, medium: 1, low: 2 }

  // Sort by priority
  const sortedTasks = [...incompleteTasks].sort((a, b) => {
    const aPriority = priorityOrder[a.priority || 'medium']
    const bPriority = priorityOrder[b.priority || 'medium']
    return aPriority - bPriority
  })

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Select a task to focus on:
      </h3>
      <div className="max-h-64 space-y-2 overflow-y-auto">
        {sortedTasks.map((task) => (
          <button
            key={task.id}
            onClick={() => onSelect(task.id)}
            className={[
              'w-full rounded-lg border p-3 text-left transition-all',
              selectedTaskId === task.id
                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200 dark:border-blue-400 dark:bg-blue-900/20 dark:ring-blue-800'
                : 'border-gray-200 bg-white hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600',
            ].join(' ')}
          >
            <div className="flex items-center gap-3">
              {/* Priority indicator */}
              <div
                className={[
                  'h-3 w-3 rounded-full',
                  task.priority === 'high'
                    ? 'bg-red-500'
                    : task.priority === 'medium'
                    ? 'bg-yellow-500'
                    : 'bg-gray-400',
                ].join(' ')}
              />
              <div className="flex-1 min-w-0">
                <p className="truncate font-medium text-gray-900 dark:text-gray-100">
                  {task.title}
                </p>
                {task.estimatedDuration && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ~{task.estimatedDuration} min
                  </p>
                )}
              </div>
              {selectedTaskId === task.id && (
                <svg
                  className="h-5 w-5 text-blue-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
