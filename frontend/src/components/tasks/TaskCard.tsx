'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import type { Task } from '@/lib/schemas/task.schema'
import type { Subtask } from '@/lib/schemas/subtask.schema'
import { useSubtasks } from '@/lib/hooks/useSubtasks'
import { useToast } from '@/lib/hooks/useToast'
import { useFocusModeStore } from '@/lib/stores/focus-mode.store'
import { usePendingCompletionsStore } from '@/lib/stores/usePendingCompletionsStore'
import { formatDistanceToNow } from 'date-fns'

/**
 * Task card component
 *
 * Displays a single task with:
 * - Title and description
 * - Priority indicator
 * - Tags
 * - Due date
 * - Checkbox that queues completion (not instant)
 * - Expandable dropdown to show subtasks (at bottom)
 * - Progress indicator (if has subtasks)
 * - Green background when marked for completion
 */

interface TaskCardProps {
  task: Task
  showProgress?: boolean
}

export function TaskCard({ task, showProgress = false }: TaskCardProps) {
  const router = useRouter()
  const { toast } = useToast()
  const { activate: activateFocusMode } = useFocusModeStore()
  const { togglePending, hasPending } = usePendingCompletionsStore()
  const [isExpanded, setIsExpanded] = useState(false)
  const subtasksQuery = useSubtasks(task.id)
  const subtasks = subtasksQuery?.data?.data || []
  const cardRef = useRef<HTMLDivElement>(null)

  const isPending = hasPending(task.id)
  const incompleteSubtasks = subtasks.filter((st: Subtask) => !st.completed)
  const hasIncompleteSubtasks = incompleteSubtasks.length > 0

  // Use schema fields for subtask counts when available (avoids extra API call in list view)
  // Fall back to fetched subtasks for expanded view
  const hasSubtaskCounts = typeof task.subtask_count === 'number'
  const subtaskCount = hasSubtaskCounts ? task.subtask_count! : subtasks.length
  const subtaskCompletedCount = hasSubtaskCounts
    ? task.subtask_completed_count!
    : subtasks.filter((st: Subtask) => st.completed).length

  // Handle click outside to collapse subtasks
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (cardRef.current && !cardRef.current.contains(event.target as Node)) {
        setIsExpanded(false)
      }
    }

    if (isExpanded) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }
  }, [isExpanded])

  const priorityColors = {
    high: 'border-l-4 border-l-red-500',
    medium: 'border-l-4 border-l-yellow-500',
    low: 'border-l-4 border-l-green-500',
  }

  const priorityBadgeColors = {
    high: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300',
    low: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300',
  }

  const handleToggleComplete = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Toggle pending - visual feedback via green background is sufficient
    togglePending(task.id)
  }

  const handleToggleExpand = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsExpanded(!isExpanded)
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

  const handleActivateFocusMode = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    activateFocusMode(task.id)
    router.push('/dashboard/focus')
    // Navigation to focus page provides sufficient feedback
  }

  // Calculate total duration from subtasks (not implemented in schema yet)
  const totalSubtaskDuration = 0

  return (
    <div ref={cardRef} className="relative">
      <Link href={`/dashboard/tasks/${task.id}`}>
        <div
          className={[
            'group relative rounded-lg border p-4',
            'transition-all duration-200',
            task.completed && 'opacity-60',
            // Pending state - green background
            isPending
              ? 'border-green-400 bg-green-50 dark:border-green-600 dark:bg-green-950/50'
              : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700',
            priorityColors[task.priority || 'low'],
          ]
            .filter(Boolean)
            .join(' ')}
        >
          <div className="flex items-start gap-3">
            {/* Checkbox - marks for pending completion */}
            <button
              onClick={handleToggleComplete}
              className={[
                'mt-0.5 h-5 w-5 flex-shrink-0 rounded border-2',
                'transition-all duration-150',
                isPending
                  ? 'border-green-500 bg-green-500'
                  : task.completed
                    ? 'border-blue-600 bg-blue-600'
                    : 'border-gray-300 bg-white dark:border-gray-600 dark:bg-gray-800',
                'hover:border-green-500',
                'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
              ]
                .filter(Boolean)
                .join(' ')}
              aria-label={isPending ? 'Unmark for completion' : 'Mark for completion'}
            >
              {(isPending || task.completed) && (
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

            <div className="flex-1 min-w-0">
              {/* Focus Mode button - only show for incomplete tasks */}
              {!task.completed && (
                <button
                  onClick={handleActivateFocusMode}
                  className={[
                    'absolute top-3 right-3 p-1.5 rounded-md opacity-0 group-hover:opacity-100',
                    'text-gray-400 hover:text-blue-600 hover:bg-blue-50',
                    'dark:text-gray-500 dark:hover:text-blue-400 dark:hover:bg-blue-900/30',
                    'transition-all duration-150',
                    'focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2',
                  ].join(' ')}
                  aria-label="Start Focus Mode for this task"
                  title="Start Focus Mode"
                >
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
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
                </button>
              )}

              {/* Title */}
              <h3
                className={[
                  'text-base font-medium',
                  isPending
                    ? 'text-green-900 dark:text-green-100'
                    : 'text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400',
                  'transition-colors',
                  task.completed && 'line-through',
                ]
                  .filter(Boolean)
                  .join(' ')}
              >
                {task.title}
                {isPending && (
                  <span className="ml-2 text-xs text-green-600 dark:text-green-400 font-normal">
                    (pending save)
                  </span>
                )}
              </h3>

              {/* Description */}
              {task.description && (
                <p
                  className={[
                    'mt-1 text-sm line-clamp-2',
                    isPending
                      ? 'text-green-700 dark:text-green-300'
                      : 'text-gray-600 dark:text-gray-400',
                  ].join(' ')}
                >
                  {task.description}
                </p>
              )}

              {/* Meta info */}
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                {/* Priority badge */}
                <span
                  className={[
                    'rounded-full px-2 py-0.5 font-medium',
                    priorityBadgeColors[task.priority || 'low'],
                  ]
                    .filter(Boolean)
                    .join(' ')}
                >
                  {task.priority || 'low'}
                </span>

                {/* Subtasks progress - uses schema fields (subtask_count, subtask_completed_count) when available */}
                {subtaskCount > 0 && (
                  <span
                    className={
                      isPending
                        ? 'text-green-700 dark:text-green-300'
                        : 'text-gray-600 dark:text-gray-400'
                    }
                    title={`${subtaskCompletedCount} of ${subtaskCount} subtasks completed`}
                  >
                    <svg
                      className="inline h-3.5 w-3.5 mr-1"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                    {subtaskCompletedCount}/{subtaskCount} subtasks
                  </span>
                )}

                {/* Duration */}
                {(task.estimated_duration || totalSubtaskDuration > 0) && (
                  <span
                    className={
                      isPending
                        ? 'text-green-700 dark:text-green-300'
                        : 'text-gray-600 dark:text-gray-400'
                    }
                  >
                    <svg
                      className="inline h-3.5 w-3.5 mr-1"
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
                    {totalSubtaskDuration > 0 ? totalSubtaskDuration : task.estimated_duration} min
                  </span>
                )}

                {/* Due date */}
                {task.due_date && (
                  <span className={getDueDateColor(task.due_date)}>
                    <svg
                      className="inline h-3.5 w-3.5 mr-1"
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
                    {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
                  </span>
                )}

                {/* Recurring indicator - TODO: Add recurrence to Task schema */}
                {/* {task.recurrence?.enabled && (
                  <span className="text-purple-600 dark:text-purple-400">
                    <svg
                      className="inline h-3.5 w-3.5 mr-1"
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
                )} */}

                {/* Recurring instance indicator - TODO: Add isRecurringInstance to Task schema */}
                {/* {task.isRecurringInstance && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2 py-0.5 text-purple-700 dark:bg-purple-900 dark:text-purple-300"
                    title="This task was generated from a recurring task"
                  >
                    <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Instance
                  </span>
                )} */}

                {/* Tags - TODO: Add tags to Task schema */}
                {/* {task.tags && task.tags.length > 0 && (
                  <>
                    {task.tags.slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                      >
                        #{tag}
                      </span>
                    ))}
                    {task.tags.length > 3 && (
                      <span className="text-gray-500">+{task.tags.length - 3}</span>
                    )}
                  </>
                )} */}
              </div>
            </div>
          </div>

          {/* Expand/Collapse button at bottom - only show if we have subtasks to display */}
          {subtaskCount > 0 && (
            <button
              onClick={handleToggleExpand}
              className={[
                'mt-3 w-full flex items-center justify-center gap-1 py-1.5 rounded-md',
                'text-xs font-medium',
                isPending
                  ? 'text-green-700 hover:bg-green-100 dark:text-green-300 dark:hover:bg-green-900/50'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800',
                'transition-all duration-150',
                'focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2',
              ].join(' ')}
              aria-label={isExpanded ? 'Collapse subtasks' : 'Expand subtasks'}
            >
              <span>
                {isExpanded ? 'Hide' : 'Show'} {subtaskCount} subtask
                {subtaskCount > 1 ? 's' : ''}
              </span>
              <svg
                className={`h-4 w-4 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
          )}
        </div>
      </Link>

      {/* Expanded subtasks section - full width, outside the link */}
      {isExpanded && subtasks.length > 0 && (
        <div
          className={[
            'mt-1 space-y-1 rounded-lg border p-3',
            isPending
              ? 'border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/30'
              : 'border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-gray-900/50',
          ].join(' ')}
        >
          <h4
            className={[
              'text-xs font-semibold uppercase tracking-wide mb-2',
              isPending
                ? 'text-green-600 dark:text-green-400'
                : 'text-gray-500 dark:text-gray-400',
            ].join(' ')}
          >
            Subtasks ({subtasks.filter((st: Subtask) => st.completed).length}/{subtasks.length})
          </h4>
          {subtasks.map((subtask: Subtask) => (
            <div key={subtask.id} className="flex items-center gap-2 py-1">
              <div
                className={[
                  'h-3.5 w-3.5 rounded border',
                  subtask.completed
                    ? 'border-green-500 bg-green-500'
                    : 'border-gray-300 dark:border-gray-600',
                ].join(' ')}
              >
                {subtask.completed && (
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
              </div>
              <span
                className={[
                  'text-sm',
                  subtask.completed
                    ? 'text-gray-400 line-through dark:text-gray-500'
                    : isPending
                      ? 'text-green-800 dark:text-green-200'
                      : 'text-gray-700 dark:text-gray-300',
                ].join(' ')}
              >
                {subtask.title}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
