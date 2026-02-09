'use client'

import { useState } from 'react'
import type { SubTask } from '@/lib/schemas/subtask.schema'
import { useUpdateSubtask, useDeleteSubtask } from '@/lib/hooks/useSubtasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'

interface SubTaskListProps {
  taskId: string
  subtasks: SubTask[]
}

export function SubTaskList({ taskId, subtasks }: SubTaskListProps) {
  const { toast } = useToast()
  const updateSubTask = useUpdateSubtask()
  const deleteSubTask = useDeleteSubtask()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleToggleComplete = async (subtask: SubTask) => {
    try {
      await updateSubTask.mutateAsync({
        taskId,
        subtaskId: subtask.id,
        input: { completed: !subtask.completed },
      })

      toast({
        title: subtask.completed ? 'Subtask reopened' : 'Subtask completed!',
        description: subtask.completed
          ? 'Subtask marked as incomplete'
          : 'Keep going! You\'re making progress.',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update subtask',
        variant: 'error',
      })
    }
  }

  const handleDelete = async (subtaskId: string) => {
    if (!confirm('Are you sure you want to delete this subtask?')) {
      return
    }

    setDeletingId(subtaskId)

    try {
      await deleteSubTask.mutateAsync({ taskId, subtaskId })

      toast({
        title: 'Subtask deleted',
        description: 'Subtask has been removed',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete subtask',
        variant: 'error',
      })
    } finally {
      setDeletingId(null)
    }
  }

  if (!subtasks || subtasks.length === 0) {
    return (
      <div className="py-8 text-center text-gray-500 dark:text-gray-400">
        No subtasks yet. Add some to break down this task.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {subtasks.map((subtask) => (
        <div
          key={subtask.id}
          className="group flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-3 transition-all hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600"
        >
          {/* Checkbox */}
          <button
            onClick={() => handleToggleComplete(subtask)}
            disabled={updateSubTask.isPending}
            className="flex-shrink-0"
          >
            <div
              className={[
                'h-5 w-5 rounded border-2 transition-all',
                subtask.completed
                  ? 'border-green-500 bg-green-500'
                  : 'border-gray-300 hover:border-green-500 dark:border-gray-600 dark:hover:border-green-500',
              ].join(' ')}
            >
              {subtask.completed && (
                <svg
                  className="h-full w-full text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
          </button>

          {/* Title */}
          <div className="flex-1">
            <span
              className={[
                'text-sm text-gray-900 dark:text-gray-100',
                subtask.completed && 'line-through opacity-60',
              ].join(' ')}
            >
              {subtask.title}
            </span>
          </div>

          {/* Delete button */}
          <button
            onClick={() => handleDelete(subtask.id)}
            disabled={deletingId === subtask.id}
            className="opacity-0 transition-opacity group-hover:opacity-100"
          >
            <svg
              className="h-4 w-4 text-gray-400 hover:text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      ))}
    </div>
  )
}
