'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { format } from 'date-fns'
import { VisuallyHidden } from '@radix-ui/react-visually-hidden'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import { useTask, useUpdateTask, useDeleteTask } from '@/lib/hooks/useTasks'
import { useSubTasks } from '@/lib/hooks/useSubTasks'
import { useToast } from '@/lib/hooks/useToast'
import { useTaskDetailModalStore } from '@/lib/stores/useTaskDetailModalStore'
import { useNewTaskModalStore } from '@/lib/stores/useNewTaskModalStore'
import { useFocusModeStore } from '@/lib/stores/useFocusModeStore'
import { usePendingCompletionsStore } from '@/lib/stores/usePendingCompletionsStore'
import { SubTaskList } from './SubTaskList'

/**
 * TaskDetailModal Component
 *
 * A modal dialog for viewing task details including:
 * - Task title, description, priority, due date
 * - Subtasks with completion toggle
 * - Action buttons (complete, edit, delete, hide)
 */
export function TaskDetailModal() {
  const router = useRouter()
  const { toast } = useToast()
  const { isOpen, taskId, closeModal } = useTaskDetailModalStore()
  const openEditModal = useNewTaskModalStore((state) => state.openEdit)
  const { activate: activateFocusMode } = useFocusModeStore()
  const { togglePending, hasPending } = usePendingCompletionsStore()

  const { data: task, isLoading } = useTask(taskId || '')
  const { data: subtasks = [], isLoading: subtasksLoading } = useSubTasks(taskId || '')
  const updateTask = useUpdateTask()
  const deleteTask = useDeleteTask()
  const [isDeleting, setIsDeleting] = useState(false)

  // Check if all subtasks are completed
  const allSubtasksCompleted = subtasks.length > 0 && subtasks.every((st) => st.completed)
  const isPending = task ? hasPending(task.id) : false
  const incompleteSubtasks = subtasks.filter((st) => !st.completed)
  const hasIncompleteSubtasks = incompleteSubtasks.length > 0

  const handleToggleComplete = () => {
    if (!task) return

    // Use the pending completions system like TaskCard does
    togglePending(task.id, hasIncompleteSubtasks, incompleteSubtasks.length)

    if (!isPending) {
      toast({
        title: 'Task marked for completion',
        description: 'Click "Save Changes" to complete marked tasks',
        variant: 'success',
      })
      // Close modal so user can access the Save Changes bar
      closeModal()
    }
  }

  const handleDelete = async () => {
    if (!task) return
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

      closeModal()
    } catch {
      setIsDeleting(false)
      toast({
        title: 'Error',
        description: 'Failed to delete task',
        variant: 'error',
      })
    }
  }

  const handleHide = async () => {
    if (!task) return

    try {
      await updateTask.mutateAsync({
        id: task.id,
        input: { version: task.version, hidden: !task.hidden },
      })

      toast({
        title: task.hidden ? 'Task unhidden' : 'Task hidden',
        description: task.hidden
          ? 'Task restored to active tasks'
          : 'Task hidden from view',
        variant: 'success',
      })
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to hide task',
        variant: 'error',
      })
    }
  }

  const handleEdit = () => {
    if (!task) return
    closeModal()
    // Cast to Task since the modal accepts both Task and TaskDetail
    openEditModal(task as any)
  }

  const handleStartFocusMode = () => {
    if (!task) return
    activateFocusMode(task.id)
    closeModal()
    router.push('/dashboard/focus')
  }

  const priorityColors = {
    high: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300',
    low: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300',
  }

  const getDueDateColor = (dueDate: string | null) => {
    if (!dueDate) return 'text-gray-500'
    const due = new Date(dueDate)
    const now = new Date()
    const diffHours = (due.getTime() - now.getTime()) / (1000 * 60 * 60)

    if (diffHours < 0) return 'text-red-600 dark:text-red-400'
    if (diffHours < 24) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && closeModal()}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        {isLoading ? (
          <>
            <VisuallyHidden>
              <DialogTitle>Loading task</DialogTitle>
            </VisuallyHidden>
            <div className="flex min-h-[200px] items-center justify-center">
              <div className="text-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent mx-auto" />
                <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                  Loading task...
                </p>
              </div>
            </div>
          </>
        ) : !task ? (
          <>
            <VisuallyHidden>
              <DialogTitle>Task not found</DialogTitle>
            </VisuallyHidden>
            <div className="flex min-h-[200px] items-center justify-center">
              <div className="text-center">
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Task not found
                </h2>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  The task may have been deleted.
                </p>
              </div>
            </div>
          </>
        ) : (
          <>
            <DialogHeader>
              <div className="flex items-start gap-3 pr-8">
                {/* Completion checkbox - square like TaskCard */}
                <button
                  onClick={handleToggleComplete}
                  className={[
                    'mt-1 h-6 w-6 shrink-0 rounded border-2',
                    'transition-all duration-150',
                    isPending
                      ? 'border-green-500 bg-green-500'
                      : task.completed
                        ? 'border-blue-600 bg-blue-600'
                        : 'border-gray-300 bg-white dark:border-gray-600 dark:bg-gray-800',
                    'hover:border-green-500',
                    'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                  ].join(' ')}
                  aria-label={isPending ? 'Unmark for completion' : 'Mark for completion'}
                >
                  {(isPending || task.completed) && (
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
                </button>

                <div className="flex-1">
                  <DialogTitle
                    className={[
                      'text-xl',
                      (task.completed || isPending) && 'line-through opacity-60',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    {task.title}
                    {isPending && (
                      <span className="ml-2 text-sm text-green-600 dark:text-green-400 font-normal">
                        (pending save)
                      </span>
                    )}
                  </DialogTitle>
                </div>
              </div>
            </DialogHeader>

            <div className="mt-4 space-y-4">
              {/* Description */}
              {task.description && (
                <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {task.description}
                </p>
              )}

              {/* Metadata row */}
              <div className="flex flex-wrap items-center gap-2 text-sm">
                {/* Priority badge */}
                <span
                  className={[
                    'rounded-full px-2.5 py-0.5 font-medium',
                    priorityColors[task.priority || 'low'],
                  ].join(' ')}
                >
                  {task.priority || 'low'} priority
                </span>

                {/* Due date */}
                {task.dueDate && (
                  <span className={getDueDateColor(task.dueDate)}>
                    <svg
                      className="inline h-4 w-4 mr-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    {format(new Date(task.dueDate), 'PPP p')}
                  </span>
                )}

                {/* Estimated duration */}
                {task.estimatedDuration && (
                  <span className="text-gray-600 dark:text-gray-400">
                    <svg
                      className="inline h-4 w-4 mr-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {task.estimatedDuration} min
                  </span>
                )}

                {/* Recurring indicator */}
                {task.recurrence?.enabled && (
                  <span className="text-purple-600 dark:text-purple-400">
                    <svg
                      className="inline h-4 w-4 mr-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    {task.recurrence.humanReadable || 'Recurring'}
                  </span>
                )}
              </div>

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {task.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Subtasks section */}
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    Subtasks {subtasks.length > 0 && `(${subtasks.filter((st) => st.completed).length}/${subtasks.length})`}
                  </h3>
                  {allSubtasksCompleted && subtasks.length > 0 && !task.completed && !isPending && (
                    <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                      All done! Mark task complete?
                    </span>
                  )}
                </div>
                {subtasksLoading ? (
                  <div className="py-4 text-center text-sm text-gray-500">Loading subtasks...</div>
                ) : subtasks.length > 0 ? (
                  <SubTaskList taskId={task.id} subtasks={subtasks} />
                ) : (
                  <p className="py-2 text-sm text-gray-500 dark:text-gray-400">
                    No subtasks yet. Use Edit to add subtasks.
                  </p>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap gap-2 border-t border-gray-200 pt-4 dark:border-gray-700">
                <Button
                  onClick={handleToggleComplete}
                  variant={isPending ? 'success' : task.completed ? 'outline' : 'primary'}
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
                      Reopen
                    </>
                  ) : isPending ? (
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
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                      Unmark
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
                      Complete
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
                    Focus Mode
                  </Button>
                )}

                <Button variant="outline" size="sm" onClick={handleEdit}>
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
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit
                </Button>

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
                  className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950 ml-auto"
                >
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
