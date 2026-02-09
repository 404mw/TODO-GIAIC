'use client'

import { X, Trophy, Lock, Star, Target, Flame, Eye, FileText, Calendar, TrendingUp } from 'lucide-react'
import type { AchievementDefinition } from '@/lib/schemas/achievement.schema'
import type { AchievementCategory } from '@/lib/schemas/common.schema'

interface AchievementDetailModalProps {
  achievement: AchievementDefinition
  isUnlocked: boolean
  userProgress?: number
  unlockedAt?: string
  onClose: () => void
}

/**
 * Achievement Detail Modal
 *
 * Displays detailed information about an achievement:
 * - Large icon and name
 * - Full description
 * - Progress bar (if locked)
 * - Unlock date (if unlocked)
 * - Tips on how to unlock
 * - Perk rewards
 */
export function AchievementDetailModal({
  achievement,
  isUnlocked,
  userProgress = 0,
  unlockedAt,
  onClose,
}: AchievementDetailModalProps) {
  const getCategoryIcon = (category: AchievementCategory) => {
    const iconClass = 'h-12 w-12'
    switch (category) {
      case 'tasks':
        return <Target className={iconClass} />
      case 'streaks':
        return <Flame className={iconClass} />
      case 'focus':
        return <Eye className={iconClass} />
      case 'notes':
        return <FileText className={iconClass} />
    }
  }

  const getCategoryColor = (category: AchievementCategory) => {
    switch (category) {
      case 'tasks':
        return {
          bg: 'bg-blue-100 dark:bg-blue-900/30',
          text: 'text-blue-600 dark:text-blue-400',
          border: 'border-blue-200 dark:border-blue-800',
          gradient: 'from-blue-500 to-blue-600',
          progress: 'bg-blue-500',
        }
      case 'streaks':
        return {
          bg: 'bg-orange-100 dark:bg-orange-900/30',
          text: 'text-orange-600 dark:text-orange-400',
          border: 'border-orange-200 dark:border-orange-800',
          gradient: 'from-orange-500 to-red-600',
          progress: 'bg-orange-500',
        }
      case 'focus':
        return {
          bg: 'bg-purple-100 dark:bg-purple-900/30',
          text: 'text-purple-600 dark:text-purple-400',
          border: 'border-purple-200 dark:border-purple-800',
          gradient: 'from-purple-500 to-purple-600',
          progress: 'bg-purple-500',
        }
      case 'notes':
        return {
          bg: 'bg-green-100 dark:bg-green-900/30',
          text: 'text-green-600 dark:text-green-400',
          border: 'border-green-200 dark:border-green-800',
          gradient: 'from-green-500 to-green-600',
          progress: 'bg-green-500',
        }
    }
  }

  const colors = getCategoryColor(achievement.category)
  const progress = Math.min((userProgress / achievement.threshold) * 100, 100)

  const getTips = (category: AchievementCategory, threshold: number): string[] => {
    switch (category) {
      case 'tasks':
        return [
          `Complete ${threshold} tasks to unlock this achievement`,
          'Focus on completing high-priority tasks first',
          'Break large tasks into smaller subtasks for faster progress',
        ]
      case 'streaks':
        return [
          `Maintain a ${threshold}-day consistency streak`,
          'Complete at least one task every day',
          "You have one grace day if you miss a day - don't break the chain!",
        ]
      case 'focus':
        return [
          `Complete ${threshold} focus mode sessions`,
          'Use focus mode for deep work and concentration',
          'Turn off distractions and commit to the timer',
        ]
      case 'notes':
        return [
          `Convert ${threshold} notes to tasks`,
          'Capture ideas in notes, then convert actionable ones to tasks',
          'Use notes for brainstorming and task planning',
        ]
      default:
        return []
    }
  }

  const formatDate = (dateString?: string): string => {
    if (!dateString) return ''
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    } catch {
      return dateString
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="relative w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 pointer-events-auto overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header with gradient background */}
          <div className={`relative bg-linear-to-br ${colors.gradient} p-8 text-white`}>
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>

            {/* Achievement Icon */}
            <div className="flex items-center justify-center mb-6">
              <div
                className={`flex items-center justify-center w-24 h-24 rounded-full ${
                  isUnlocked ? 'bg-white/20' : 'bg-black/20'
                }`}
              >
                {isUnlocked ? (
                  <Trophy className="h-14 w-14" />
                ) : (
                  <Lock className="h-14 w-14" />
                )}
              </div>
            </div>

            {/* Achievement Name */}
            <h2 className="text-3xl font-bold text-center mb-2">{achievement.name}</h2>

            {/* Category Badge */}
            <div className="flex items-center justify-center gap-2 text-white/90">
              {getCategoryIcon(achievement.category)}
              <span className="text-lg capitalize">{achievement.category}</span>
            </div>

            {/* Status Badge */}
            {isUnlocked && (
              <div className="flex items-center justify-center gap-2 mt-4">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm">
                  <Trophy className="h-4 w-4" />
                  <span className="font-medium">Unlocked</span>
                </div>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-8 space-y-6">
            {/* Description */}
            <div>
              <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                Description
              </h3>
              <p className="text-gray-900 dark:text-gray-100 leading-relaxed">
                {achievement.message}
              </p>
            </div>

            {/* Progress (if locked) */}
            {!isUnlocked && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
                  Your Progress
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      {userProgress} / {achievement.threshold}
                    </span>
                    <span className={`font-semibold ${colors.text}`}>
                      {Math.round(progress)}%
                    </span>
                  </div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${colors.progress} transition-all duration-500 rounded-full`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <TrendingUp className="h-4 w-4" />
                    <span>
                      {achievement.threshold - userProgress} more to unlock
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Unlock Date (if unlocked) */}
            {isUnlocked && unlockedAt && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                  Unlocked
                </h3>
                <div className="flex items-center gap-2 text-gray-900 dark:text-gray-100">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <span>{formatDate(unlockedAt)}</span>
                </div>
              </div>
            )}

            {/* Perk Reward */}
            {achievement.perk_type && achievement.perk_value && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
                  Reward
                </h3>
                <div className="flex items-center gap-3 p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/50">
                    <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-gray-100">
                      +{achievement.perk_value}{' '}
                      {achievement.perk_type.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Permanent account upgrade
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Tips (if locked) */}
            {!isUnlocked && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
                  How to Unlock
                </h3>
                <ul className="space-y-2">
                  {getTips(achievement.category, achievement.threshold).map((tip, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-400"
                    >
                      <span className={`flex-shrink-0 w-5 h-5 rounded-full ${colors.bg} ${colors.text} flex items-center justify-center text-xs font-bold mt-0.5`}>
                        {index + 1}
                      </span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Button */}
            <div className="pt-4">
              <button
                onClick={onClose}
                className="w-full py-3 px-6 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
