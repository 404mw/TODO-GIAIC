'use client'

/**
 * Achievement Progress Component
 *
 * Displays a progress bar showing current progress toward unlocking an achievement.
 * Includes visual indicators when close to unlocking (90%+ progress).
 */

interface AchievementProgressProps {
  current: number
  threshold: number
  className?: string
}

export function AchievementProgressBar({ current, threshold, className = '' }: AchievementProgressProps) {
  const percentage = Math.min(100, Math.round((current / threshold) * 100))
  const isCloseToUnlocking = percentage >= 90

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-600 dark:text-gray-400">
          {current} / {threshold}
        </span>
        <span className={`font-medium ${isCloseToUnlocking ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'}`}>
          {percentage}%
        </span>
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`absolute left-0 top-0 h-full rounded-full transition-all duration-500 ${
            isCloseToUnlocking
              ? 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg shadow-green-500/50'
              : 'bg-gradient-to-r from-blue-500 to-purple-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
        {isCloseToUnlocking && (
          <div className="absolute right-0 top-0 h-full w-1/3 animate-pulse bg-gradient-to-l from-green-400/30 to-transparent" />
        )}
      </div>
    </div>
  )
}
