'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { format } from 'date-fns'
import type { Task } from '@/lib/schemas/task.schema'
import { useUpdateTask, useDeleteTask } from '@/lib/hooks/useTasks'
import { useSubtasks } from '@/lib/hooks/useSubtasks'
import { useToast } from '@/lib/hooks/useToast'
import { useNewTaskModalStore } from '@/lib/stores/useNewTaskModalStore'
import { useFocusStore } from '@/lib/stores/useFocusStore'
import { Button } from '@/components/ui/Button'
import { SubTaskList } from './SubTaskList'
import { TaskMetadata } from './TaskMetadata'
import { ReminderSection } from '@/components/reminders/ReminderSection'
import type { ReminderCreate } from '@/lib/schemas/reminder.schema'

interface TaskDetailViewProps {
  task: Task
}

export function TaskDetailView({ task }: TaskDetailViewProps) {
  const router = useRouter()
  const { toast } = useToast()
  const updateTask = useUpdateTask()
  const deleteTask = useDeleteTask()
  const { data: subtasks = [], isLoading: subtasksLoading } = useSubtasks(task.id)
  const [isDeleting, setIsDeleting] = useState(false)
  const openEditModal = useNewTaskModalStore((state) => state.openEdit)
  const { activate: activateFocusMode } = useFocusStore()

  const handleToggleComplete = async () => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        input: { completed: !task.completed },
      })

      toast({
        title: task.completed ? 'Task reopened' : 'Task completed!',
        description: task.completed
          ? 'Task marked as incomplete'
          : 'Great work! Keep up the momentum.',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update task',
        variant: 'error',
      })
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return
    }

    setIsDeleting(true)

    try {
      await deleteTask.mutateAsync(task.id)

      toast({
        title: 'Task deleted',
        description: 'Task has been permanently deleted',
        variant: 'success',
      })

      router.push('/dashboard/tasks')
    } catch (error) {
      setIsDeleting(false)
      toast({
        title: 'Error',
        description: 'Failed to delete task',
        variant: 'error',
      })
    }
  }

  const handleHide = async () => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        input: { hidden: !task.hidden },
      })

      toast({
        title: task.hidden ? 'Task unhidden' : 'Task hidden',
        description: task.hidden
          ? 'Task restored to active tasks'
          : 'Task hidden from view',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to hide task',
        variant: 'error',
      })
    }
  }

  const handleEdit = () => {
    openEditModal(task)
  }

  const handleStartFocusMode = () => {
    activateFocusMode(task.id)
    router.push('/dashboard/focus')
  }

  const handleAddReminder = async (reminder: ReminderCreate) => {
    try {
      // Call your API to create reminder
      // await createReminder(reminder)

      toast({
        title: 'Reminder added',
        description: "You'll be notified before the task is due",
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create reminder',
        variant: 'error',
      })
    }
  }

  const handleDeleteReminder = async (reminderId: string) => {
    try {
      // Call your API to delete reminder
      // await deleteReminder(reminderId)

      toast({
        title: 'Reminder deleted',
        description: 'Reminder has been removed',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete reminder',
        variant: 'error',
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
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

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleHide}
              disabled={updateTask.isPending}
            >
              {task.hidden ? 'Unhide' : 'Hide'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
            <Button variant="outline" size="sm" onClick={handleEdit}>
              Edit
            </Button>
          </div>
        </div>

        {/* Task Content */}
        <div className="space-y-6">
          {/* Title, completion checkbox, and action buttons */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-start gap-4">
              <button
                onClick={handleToggleComplete}
                disabled={updateTask.isPending}
                className="mt-1 shrink-0"
              >
                <div
                  className={[
                    'h-6 w-6 rounded-full border-2 transition-all',
                    task.completed
                      ? 'border-green-500 bg-green-500'
                      : 'border-gray-300 hover:border-green-500 dark:border-gray-600 dark:hover:border-green-500',
                  ].join(' ')}
                >
                  {task.completed && (
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

              <div className="flex-1">
                <h1
                  className={[
                    'text-3xl font-bold text-gray-900 dark:text-gray-100',
                    task.completed && 'line-through opacity-60',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                >
                  {task.title}
                </h1>

                {task.description && (
                  <p className="mt-3 text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {task.description}
                  </p>
                )}

                {/* Action buttons */}
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button
                    onClick={handleToggleComplete}
                    disabled={updateTask.isPending}
                    variant={task.completed ? 'outline' : 'primary'}
                    size="sm"
                  >
                    {task.completed ? (
                      <>
                        <svg
                          className="mr-1.5 h-4 w-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                          />
                        </svg>
                        Reopen Task
                      </>
                    ) : (
                      <>
                        <svg
                          className="mr-1.5 h-4 w-4"
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
                        Mark Complete
                      </>
                    )}
                  </Button>

                  {!task.completed && (
                    <Button
                      onClick={handleStartFocusMode}
                      variant="outline"
                      size="sm"
                      className="bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800 dark:hover:bg-purple-900"
                    >
                      <svg
                        className="mr-1.5 h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
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
                      Start Focus Mode
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <TaskMetadata task={task} />

          {/* Recurrence Section (T112) */}
          {task.recurrence?.enabled && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
                    <svg
                      className="h-5 w-5 text-blue-600 dark:text-blue-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    Recurring Task
                  </h2>

                  {/* Human-Readable Description */}
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Schedule:</span>{' '}
                      {task.recurrence.humanReadable}
                    </p>
                  </div>

                  {/* Next Scheduled Date */}
                  {task.recurrence.nextScheduledDate && (
                    <div className="mb-3">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-medium">Next occurrence:</span>{' '}
                        {format(new Date(task.recurrence.nextScheduledDate), 'PPP p')}
                      </p>
                    </div>
                  )}

                  {/* Instance Generation Mode */}
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Generation:</span> On completion
                    </p>
                  </div>

                  {/* Parent Task Link (if this is a recurring instance) */}
                  {task.isRecurringInstance && task.parentRecurringTaskId && (
                    <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950">
                      <p className="mb-2 text-sm font-medium text-blue-900 dark:text-blue-100">
                        This is a recurring instance
                      </p>
                      <Link
                        href={`/dashboard/tasks/${task.parentRecurringTaskId}`}
                        className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        View parent recurring task →
                      </Link>
                    </div>
                  )}
                </div>

                {/* Edit Recurrence Button */}
                <Button variant="outline" size="sm" onClick={handleEdit}>
                  <svg
                    className="mr-1 h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit
                </Button>
              </div>
            </div>
          )}

          {/* Subtasks */}
          {!subtasksLoading && subtasks.length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
                Subtasks ({subtasks.filter((st) => st.completed).length}/
                {subtasks.length})
              </h2>
              <SubTaskList taskId={task.id} subtasks={subtasks} />
            </div>
          )}

          {/* Reminders */}
          <ReminderSection
            task={task}
            onAddReminder={handleAddReminder}
            onDeleteReminder={handleDeleteReminder}
          />

          {/* Activity log placeholder */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Activity
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Activity log will be displayed here
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
