'use client'

/**
 * TaskProgressBar component
 *
 * Displays sub-task completion progress as a visual bar.
 * Only renders when there are sub-tasks (hidden when 0 sub-tasks per FR-004).
 *
 * Features:
 * - Visual progress bar with percentage
 * - Color changes based on completion (gray -> blue -> green)
 * - Accessible with aria-label
 */

interface TaskProgressBarProps {
  /** Total number of sub-tasks */
  total: number
  /** Number of completed sub-tasks */
  completed: number
  /** Show percentage text (default: true) */
  showPercentage?: boolean
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
}

export function TaskProgressBar({
  total,
  completed,
  showPercentage = true,
  size = 'md',
}: TaskProgressBarProps) {
  // Don't render if no sub-tasks (FR-004)
  if (total === 0) {
    return null
  }

  // Calculate percentage
  const percentage = Math.round((completed / total) * 100)

  // Determine color based on progress
  const getColor = () => {
    if (percentage === 100) return 'bg-green-500'
    if (percentage >= 50) return 'bg-blue-500'
    return 'bg-gray-400'
  }

  // Size variants
  const heights = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  return (
    <div className="w-full">
      <div className="flex items-center gap-2">
        {/* Progress bar container */}
        <div
          className={`flex-1 rounded-full bg-gray-200 dark:bg-gray-700 ${heights[size]}`}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${completed} of ${total} sub-tasks completed`}
        >
          {/* Progress bar fill */}
          <div
            className={`${heights[size]} rounded-full transition-all duration-300 ease-out ${getColor()}`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Percentage text */}
        {showPercentage && (
          <span className="min-w-[3rem] text-right text-xs text-gray-500 dark:text-gray-400">
            {percentage}%
          </span>
        )}
      </div>

      {/* Sub-task count */}
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {completed} of {total} sub-tasks
      </p>
    </div>
  )
}
