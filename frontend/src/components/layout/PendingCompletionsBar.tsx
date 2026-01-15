'use client'

import { useState } from 'react'
import { usePendingCompletionsStore } from '@/lib/stores/usePendingCompletionsStore'
import { useUpdateTask } from '@/lib/hooks/useTasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'

/**
 * Fixed bottom bar for pending task completions
 *
 * Displays when there are pending task completions and persists across tabs.
 * Shows warning when trying to save tasks with incomplete subtasks.
 */

export function PendingCompletionsBar() {
  const [isSaving, setIsSaving] = useState(false)
  const {
    getPendingIds,
    getPendingCount,
    clearPending,
    hasTasksWithIncompleteSubtasks,
    getTasksWithIncompleteSubtasks,
    showWarning,
    setShowWarning,
  } = usePendingCompletionsStore()
  const updateTask = useUpdateTask()
  const { toast } = useToast()

  const pendingCount = getPendingCount()
  const tasksWithIncompleteSubtasks = getTasksWithIncompleteSubtasks()
  const totalIncompleteSubtasks = tasksWithIncompleteSubtasks.reduce(
    (acc, t) => acc + t.incompleteSubtasksCount,
    0
  )

  if (pendingCount === 0) return null

  const handleSaveCompletions = async () => {
    // First click - check for incomplete subtasks and show warning
    if (hasTasksWithIncompleteSubtasks() && !showWarning) {
      setShowWarning(true)
      return
    }

    // Second click (after warning) or no incomplete subtasks - proceed with save
    const pendingIds = getPendingIds()
    if (pendingIds.length === 0) return

    setIsSaving(true)
    let successCount = 0
    let errorCount = 0

    for (const taskId of pendingIds) {
      try {
        await updateTask.mutateAsync({
          id: taskId,
          input: { completed: true },
        })
        successCount++
      } catch {
        errorCount++
      }
    }

    setIsSaving(false)
    clearPending()

    if (errorCount === 0) {
      toast({
        title: 'Tasks completed!',
        description: `${successCount} task${successCount > 1 ? 's' : ''} marked as complete`,
        variant: 'success',
      })
    } else {
      toast({
        title: 'Partial success',
        description: `${successCount} completed, ${errorCount} failed`,
        variant: 'error',
      })
    }
  }

  const handleDiscardPending = () => {
    clearPending()
    toast({
      title: 'Changes discarded',
      description: 'Pending completions have been cleared',
      variant: 'success',
    })
  }

  return (
    <div className="fixed bottom-4 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none">
      <div
        className={[
          'pointer-events-auto rounded-lg border shadow-lg',
          'transition-all duration-300 ease-in-out',
          'max-w-xl w-full',
          showWarning
            ? 'border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-950'
            : 'border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950',
        ].join(' ')}
      >
        <div className="px-4 py-3">
          <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            {showWarning ? (
              <>
                <svg
                  className="h-5 w-5 text-red-600 dark:text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span className="text-sm font-medium text-red-800 dark:text-red-200">
                  {tasksWithIncompleteSubtasks.length} task
                  {tasksWithIncompleteSubtasks.length > 1 ? 's' : ''} ha
                  {tasksWithIncompleteSubtasks.length > 1 ? 've' : 's'}{' '}
                  {totalIncompleteSubtasks} incomplete subtask
                  {totalIncompleteSubtasks > 1 ? 's' : ''}. Complete anyway?
                </span>
              </>
            ) : (
              <>
                <svg
                  className="h-5 w-5 text-green-600 dark:text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span className="text-sm font-medium text-green-800 dark:text-green-200">
                  {pendingCount} task{pendingCount > 1 ? 's' : ''} marked for completion
                </span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDiscardPending}
              disabled={isSaving}
              className={
                showWarning
                  ? 'text-red-700 hover:bg-red-100 dark:text-red-300 dark:hover:bg-red-900'
                  : ''
              }
            >
              Discard
            </Button>
            <Button
              variant={showWarning ? 'danger' : 'success'}
              size="sm"
              onClick={handleSaveCompletions}
              loading={isSaving}
            >
              {showWarning ? 'Save Anyway' : 'Save Changes'}
            </Button>
          </div>
          </div>
        </div>
      </div>
    </div>
  )
}
