'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTasks, useUpdateTask } from '@/lib/hooks/useTasks'
import { useSubtasks, useUpdateSubtask } from '@/lib/hooks/useSubtasks'
import { useFocusModeStore } from '@/lib/stores/focus-mode.store'
import { useToast } from '@/lib/hooks/useToast'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { FocusTimer } from '@/components/focus/FocusTimer'
import { TaskSelector } from '@/components/focus/TaskSelector'
import { Button } from '@/components/ui/Button'
import type { SubTask } from '@/lib/schemas/subtask.schema'

/**
 * Focus Mode Page
 *
 * Features:
 * - Select a task to focus on
 * - If task has subtasks, prompt to select which subtasks to work on
 * - Duration is calculated from selected subtasks (no manual timer input)
 * - Display subtasks during focus mode for marking completion
 * - Marking doesn't complete subtasks immediately - must save
 */

export default function FocusModePage() {
  const router = useRouter()
  const { toast } = useToast()
  const { data: tasks = [], isLoading } = useTasks({ hidden: false })
  const updateTask = useUpdateTask()
  const updateSubTask = useUpdateSubtask()
  const { isActive, taskId, activate, deactivate } = useFocusModeStore()

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [selectedSubtaskIds, setSelectedSubtaskIds] = useState<Set<string>>(new Set())
  const [pendingSubtaskCompletions, setPendingSubtaskCompletions] = useState<Set<string>>(new Set())
  const [sessionStarted, setSessionStarted] = useState(false)
  const [showSubtaskSelection, setShowSubtaskSelection] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Get selected task
  const selectedTask = tasks.find((t) => t.id === selectedTaskId)

  // Fetch subtasks for selected task
  const { data: subtasks = [] } = useSubtasks(selectedTaskId || '')

  // Filter to only incomplete subtasks
  const incompleteSubtasks = subtasks.filter((st: SubTask) => !st.completed)

  // Calculate total duration from selected subtasks
  const totalDuration = Array.from(selectedSubtaskIds).reduce((acc, id) => {
    const subtask = subtasks.find((st: SubTask) => st.id === id)
    return acc + (subtask?.estimatedDuration || 0)
  }, 0)

  // Initialize from store if focus is already active
  useEffect(() => {
    if (isActive && taskId) {
      setSelectedTaskId(taskId)
      setSessionStarted(true)
    }
  }, [isActive, taskId])

  // When task is selected, check if it has subtasks
  useEffect(() => {
    if (selectedTaskId && incompleteSubtasks.length > 0) {
      setShowSubtaskSelection(true)
      // Auto-select all incomplete subtasks by default
      setSelectedSubtaskIds(new Set(incompleteSubtasks.map((st: SubTask) => st.id)))
    } else {
      setShowSubtaskSelection(false)
      setSelectedSubtaskIds(new Set())
    }
  }, [selectedTaskId, incompleteSubtasks.length])

  const handleSubtaskToggle = (subtaskId: string) => {
    setSelectedSubtaskIds((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(subtaskId)) {
        newSet.delete(subtaskId)
      } else {
        newSet.add(subtaskId)
      }
      return newSet
    })
  }

  const handleStart = () => {
    if (!selectedTaskId) {
      toast({
        title: 'Select a task',
        description: 'Please select a task to focus on',
        variant: 'error',
      })
      return
    }

    if (incompleteSubtasks.length > 0 && selectedSubtaskIds.size === 0) {
      toast({
        title: 'Select subtasks',
        description: 'Please select at least one subtask to work on',
        variant: 'error',
      })
      return
    }

    if (incompleteSubtasks.length > 0 && totalDuration === 0) {
      toast({
        title: 'No duration set',
        description: 'Selected subtasks have no estimated duration. Please add durations to subtasks first.',
        variant: 'error',
      })
      return
    }

    activate(selectedTaskId)
    setSessionStarted(true)
    setPendingSubtaskCompletions(new Set())

    const durationText = totalDuration > 0 ? `for ${totalDuration} minutes` : ''
    toast({
      title: 'Focus mode started',
      description: `Focusing on "${selectedTask?.title}" ${durationText}`,
      variant: 'success',
    })
  }

  const handlePendingSubtaskToggle = (subtaskId: string) => {
    setPendingSubtaskCompletions((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(subtaskId)) {
        newSet.delete(subtaskId)
      } else {
        newSet.add(subtaskId)
      }
      return newSet
    })
  }

  const handleSaveAndComplete = async () => {
    setIsSaving(true)

    // Save pending subtask completions
    for (const subtaskId of pendingSubtaskCompletions) {
      try {
        await updateSubTask.mutateAsync({
          taskId: selectedTaskId!,
          subtaskId,
          input: { completed: true },
        })
      } catch (error) {
        console.error('Failed to complete subtask:', error)
      }
    }

    // Ask if user wants to mark task as complete
    if (selectedTask) {
      const markComplete = confirm('Mark this task as complete?')
      if (markComplete) {
        try {
          await updateTask.mutateAsync({
            id: selectedTask.id,
            input: { completed: true },
          })
          toast({
            title: 'Task completed!',
            description: 'Great work on finishing your focus session!',
            variant: 'success',
          })
        } catch (error) {
          toast({
            title: 'Error',
            description: 'Failed to mark task as complete',
            variant: 'error',
          })
        }
      }
    }

    setIsSaving(false)
    deactivate()
    setSessionStarted(false)
    setPendingSubtaskCompletions(new Set())

    toast({
      title: 'Focus session complete!',
      description: `Completed ${pendingSubtaskCompletions.size} subtask${pendingSubtaskCompletions.size !== 1 ? 's' : ''}`,
      variant: 'success',
    })
  }

  const handleExit = () => {
    if (sessionStarted) {
      const hasUnsavedChanges = pendingSubtaskCompletions.size > 0
      const message = hasUnsavedChanges
        ? 'You have unsaved subtask completions. Are you sure you want to exit?'
        : 'Are you sure you want to exit? Your progress will be lost.'
      if (!confirm(message)) return
    }

    deactivate()
    setSessionStarted(false)
    setPendingSubtaskCompletions(new Set())
    router.push('/dashboard/tasks')
  }

  // Get subtasks that are currently being worked on (selected for this session)
  const activeSubtasks = subtasks.filter((st: SubTask) => selectedSubtaskIds.has(st.id))

  // Full-screen focus view when session is active
  if (sessionStarted && selectedTask) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
        <div className="mx-auto max-w-2xl px-4 py-12">
          {/* Exit button */}
          <div className="mb-8 flex justify-between items-center">
            {pendingSubtaskCompletions.size > 0 && (
              <span className="text-sm text-green-600 dark:text-green-400">
                {pendingSubtaskCompletions.size} subtask{pendingSubtaskCompletions.size !== 1 ? 's' : ''} marked for completion
              </span>
            )}
            <div className="ml-auto flex gap-2">
              {pendingSubtaskCompletions.size > 0 && (
                <Button
                  variant="success"
                  size="sm"
                  onClick={handleSaveAndComplete}
                  loading={isSaving}
                >
                  Save & Complete
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={handleExit}>
                <svg
                  className="mr-2 h-4 w-4"
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
                Exit
              </Button>
            </div>
          </div>

          {/* Task info */}
          <div className="mb-8 text-center">
            <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              Focusing on
            </span>
            <h1 className="mt-4 text-3xl font-bold text-gray-900 dark:text-gray-100">
              {selectedTask.title}
            </h1>
            {selectedTask.description && (
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                {selectedTask.description}
              </p>
            )}
          </div>

          {/* Timer */}
          {totalDuration > 0 ? (
            <FocusTimer
              durationMinutes={totalDuration}
              onComplete={handleSaveAndComplete}
              onExit={handleExit}
              isRunning={true}
            />
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                No timer - work at your own pace
              </p>
            </div>
          )}

          {/* Subtasks section during focus mode */}
          {activeSubtasks.length > 0 && (
            <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
              <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
                Subtasks ({pendingSubtaskCompletions.size}/{activeSubtasks.length})
              </h3>
              <div className="space-y-3">
                {activeSubtasks.map((subtask: SubTask) => {
                  const isPendingCompletion = pendingSubtaskCompletions.has(subtask.id)
                  const isAlreadyCompleted = subtask.completed

                  return (
                    <div
                      key={subtask.id}
                      className={[
                        'flex items-center gap-3 rounded-lg border p-3 transition-all',
                        isPendingCompletion
                          ? 'border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950'
                          : isAlreadyCompleted
                            ? 'border-gray-200 bg-gray-50 opacity-60 dark:border-gray-700 dark:bg-gray-900'
                            : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800',
                      ].join(' ')}
                    >
                      <button
                        onClick={() => !isAlreadyCompleted && handlePendingSubtaskToggle(subtask.id)}
                        disabled={isAlreadyCompleted}
                        className={[
                          'h-5 w-5 shrink-0 rounded border-2 transition-all',
                          isPendingCompletion || isAlreadyCompleted
                            ? 'border-green-500 bg-green-500'
                            : 'border-gray-300 hover:border-green-500 dark:border-gray-600',
                        ].join(' ')}
                      >
                        {(isPendingCompletion || isAlreadyCompleted) && (
                          <svg
                            className="h-full w-full text-white"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
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
                        <span
                          className={[
                            'text-sm',
                            isPendingCompletion || isAlreadyCompleted
                              ? 'line-through text-gray-500 dark:text-gray-400'
                              : 'text-gray-900 dark:text-gray-100',
                          ].join(' ')}
                        >
                          {subtask.title}
                        </span>
                        {isPendingCompletion && !isAlreadyCompleted && (
                          <span className="ml-2 text-xs text-green-600 dark:text-green-400">
                            (pending save)
                          </span>
                        )}
                      </div>
                      {subtask.estimatedDuration && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {subtask.estimatedDuration} min
                        </span>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Keyboard shortcuts hint */}
          <div className="mt-8 flex justify-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 font-mono">Space</kbd>
              <span>Pause/Resume</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 font-mono">Esc</kbd>
              <span>Exit</span>
            </span>
          </div>
        </div>
      </div>
    )
  }

  // Setup view
  return (
    <DashboardLayout>
      <div className="mx-auto max-w-2xl py-8">
        {/* Header */}
        <div className="mb-8">
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
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Focus Mode
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Eliminate distractions and focus on one task at a time
          </p>
        </div>

        <div className="space-y-6">
          {/* Task selection */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h3 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">
              Select a Task
            </h3>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
              </div>
            ) : (
              <TaskSelector
                tasks={tasks}
                selectedTaskId={selectedTaskId}
                onSelect={setSelectedTaskId}
              />
            )}
          </div>

          {/* Subtask selection (if task has subtasks) */}
          {showSubtaskSelection && incompleteSubtasks.length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
              <h3 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">
                Select Subtasks to Work On
              </h3>
              <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
                Duration will be calculated from selected subtasks
              </p>
              <div className="space-y-2">
                {incompleteSubtasks.map((subtask: SubTask) => (
                  <div
                    key={subtask.id}
                    className={[
                      'flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-all',
                      selectedSubtaskIds.has(subtask.id)
                        ? 'border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-950'
                        : 'border-gray-200 bg-white hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800',
                    ].join(' ')}
                    onClick={() => handleSubtaskToggle(subtask.id)}
                  >
                    <div
                      className={[
                        'h-5 w-5 shrink-0 rounded border-2 transition-all flex items-center justify-center',
                        selectedSubtaskIds.has(subtask.id)
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300 dark:border-gray-600',
                      ].join(' ')}
                    >
                      {selectedSubtaskIds.has(subtask.id) && (
                        <svg
                          className="h-3 w-3 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
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
                    <div className="flex-1">
                      <span className="text-sm text-gray-900 dark:text-gray-100">
                        {subtask.title}
                      </span>
                    </div>
                    {subtask.estimatedDuration ? (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {subtask.estimatedDuration} min
                      </span>
                    ) : (
                      <span className="text-xs text-orange-500 dark:text-orange-400">
                        No duration
                      </span>
                    )}
                  </div>
                ))}
              </div>

              {/* Total duration display */}
              <div className="mt-4 flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Total Duration
                </span>
                <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {totalDuration > 0 ? `${totalDuration} min` : 'No duration set'}
                </span>
              </div>
            </div>
          )}

          {/* Start button */}
          <Button
            onClick={handleStart}
            disabled={!selectedTaskId || isLoading || (incompleteSubtasks.length > 0 && selectedSubtaskIds.size === 0)}
            className="w-full py-6 text-lg"
          >
            {incompleteSubtasks.length > 0 && totalDuration > 0
              ? `Start Focus Session (${totalDuration} min)`
              : 'Start Focus Session'}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}
