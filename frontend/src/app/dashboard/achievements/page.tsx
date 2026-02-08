'use client'

import { useState } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useAchievements } from '@/lib/hooks/useAchievements'
import { AchievementProgressBar } from '@/components/achievements/AchievementProgress'
import type { AchievementProgress } from '@/lib/schemas/achievement.schema'

/**
 * Achievements page (US5 - FR-029 to FR-033)
 *
 * Displays user productivity metrics and achievements:
 * - User stats (lifetime tasks, current streak, focus completions)
 * - Unlocked achievements with perks
 * - Locked achievements with progress bars
 * - Effective limits based on tier and achievement perks
 * - Category filtering (tasks, streaks, focus, notes)
 */

type AchievementCategory = 'all' | 'tasks' | 'streaks' | 'focus' | 'notes'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  color: 'blue' | 'green' | 'orange' | 'purple' | 'red'
}

function MetricCard({ title, value, subtitle, icon, color }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
    purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
    red: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  }

  const shadowClasses = {
    blue: 'hover:shadow-blue-500/20 dark:hover:shadow-blue-500/10',
    green: 'hover:shadow-green-500/20 dark:hover:shadow-green-500/10',
    orange: 'hover:shadow-orange-500/20 dark:hover:shadow-orange-500/10',
    purple: 'hover:shadow-purple-500/20 dark:hover:shadow-purple-500/10',
    red: 'hover:shadow-red-500/20 dark:hover:shadow-red-500/10',
  }

  const glowClasses = {
    blue: 'group-hover:from-blue-500/5 group-hover:to-blue-500/10 dark:group-hover:from-blue-500/10 dark:group-hover:to-blue-500/5',
    green: 'group-hover:from-green-500/5 group-hover:to-green-500/10 dark:group-hover:from-green-500/10 dark:group-hover:to-green-500/5',
    orange: 'group-hover:from-orange-500/5 group-hover:to-orange-500/10 dark:group-hover:from-orange-500/10 dark:group-hover:to-orange-500/5',
    purple: 'group-hover:from-purple-500/5 group-hover:to-purple-500/10 dark:group-hover:from-purple-500/10 dark:group-hover:to-purple-500/5',
    red: 'group-hover:from-red-500/5 group-hover:to-red-500/10 dark:group-hover:from-red-500/10 dark:group-hover:to-red-500/5',
  }

  return (
    <div className={`group relative rounded-lg border border-gray-200 bg-white p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${shadowClasses[color]} dark:border-gray-800 dark:bg-gray-900`}>
      <div className={`absolute inset-0 rounded-lg bg-linear-to-br from-transparent to-transparent ${glowClasses[color]} transition-all duration-300`} />
      <div className="relative flex items-start gap-4">
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${colorClasses[color]}`}
        >
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AchievementsPage() {
  const { data: achievements, isLoading, error } = useAchievements()
  const [selectedCategory, setSelectedCategory] = useState<AchievementCategory>('all')

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200">
          <p className="font-medium">Failed to load achievements</p>
          <p className="text-sm">Please try refreshing the page.</p>
        </div>
      </DashboardLayout>
    )
  }

  const stats = achievements?.stats
  const focusCompletions = stats?.focusCompletions || 0
  const lifetimeCompleted = stats?.lifetimeTasksCompleted || 0
  const unlockedAchievements = achievements?.unlocked || []
  const allProgress = achievements?.progress || []
  const effectiveLimits = achievements?.effectiveLimits

  // Filter locked achievements (not yet unlocked)
  const lockedProgress = allProgress.filter((p) => !p.unlocked)

  // Filter by category
  const getCategoryFromId = (id: string): AchievementCategory => {
    if (id.startsWith('tasks_')) return 'tasks'
    if (id.startsWith('streak_')) return 'streaks'
    if (id.startsWith('focus_')) return 'focus'
    if (id.startsWith('notes_')) return 'notes'
    return 'all'
  }

  const filteredProgress = selectedCategory === 'all'
    ? lockedProgress
    : lockedProgress.filter((p) => getCategoryFromId(p.id) === selectedCategory)

  const filteredUnlocked = selectedCategory === 'all'
    ? unlockedAchievements
    : unlockedAchievements.filter((a) => getCategoryFromId(a.id) === selectedCategory)

  const categories: { value: AchievementCategory; label: string; icon: React.ReactNode }[] = [
    {
      value: 'all',
      label: 'All',
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      ),
    },
    {
      value: 'tasks',
      label: 'Tasks',
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      value: 'streaks',
      label: 'Streaks',
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
        </svg>
      ),
    },
    {
      value: 'focus',
      label: 'Focus',
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      value: 'notes',
      label: 'Notes',
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      ),
    },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Achievements
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Track your productivity, unlock perks, and celebrate your wins
          </p>
        </div>

        {/* Effective Limits */}
        {effectiveLimits && (
          <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-purple-50 to-pink-50 p-6 dark:border-gray-700 dark:from-purple-900/20 dark:to-pink-900/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900/50">
                <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Your Current Limits
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Unlock achievements to increase your limits
                </p>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 p-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">Max Tasks</div>
                <div className="mt-1 text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {effectiveLimits.maxTasks === -1 ? '∞' : effectiveLimits.maxTasks}
                </div>
              </div>
              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 p-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">Max Notes</div>
                <div className="mt-1 text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {effectiveLimits.maxNotes === -1 ? '∞' : effectiveLimits.maxNotes}
                </div>
              </div>
              <div className="rounded-lg bg-white/80 dark:bg-gray-900/50 p-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">Daily AI Credits</div>
                <div className="mt-1 text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {effectiveLimits.dailyAiCredits}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Streak Section */}
        <div className="rounded-xl border border-gray-200 bg-linear-to-br from-orange-50 to-yellow-50 p-6 dark:border-gray-700 dark:from-orange-900/20 dark:to-yellow-900/20">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/50">
              <svg
                className="h-8 w-8 text-orange-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Consistency Streak
              </h2>
              <p className="text-4xl font-bold text-orange-600 dark:text-orange-400">
                {stats?.currentStreak || 0} days
              </p>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Longest streak: {stats?.longestStreak || 0} days
              </p>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Lifetime Tasks"
            value={lifetimeCompleted}
            subtitle="Total tasks completed"
            color="green"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />

          <MetricCard
            title="Focus Completions"
            value={focusCompletions}
            subtitle="Tasks in focus mode"
            color="blue"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            }
          />

          <MetricCard
            title="Notes Converted"
            value={stats?.notesConverted || 0}
            subtitle="Notes to tasks"
            color="purple"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            }
          />

          <MetricCard
            title="Achievements"
            value={`${unlockedAchievements.length}/${allProgress.length}`}
            subtitle="Unlocked milestones"
            color="orange"
            icon={
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                />
              </svg>
            }
          />
        </div>

        {/* Category Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex gap-2 overflow-x-auto">
            {categories.map((category) => (
              <button
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                className={`flex items-center gap-2 whitespace-nowrap rounded-t-lg px-4 py-2 text-sm font-medium transition-colors ${
                  selectedCategory === category.value
                    ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                    : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
                }`}
              >
                {category.icon}
                {category.label}
              </button>
            ))}
          </div>
        </div>

        {/* Unlocked Achievements */}
        {filteredUnlocked.length > 0 && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Unlocked Achievements
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {filteredUnlocked.map((achievement) => (
                <div
                  key={achievement.id}
                  className="flex items-start gap-3 rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800/50 dark:bg-yellow-900/10"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                    <svg
                      className="h-6 w-6 text-yellow-600 dark:text-yellow-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        {achievement.name}
                      </p>
                      {achievement.perk && (
                        <span className="shrink-0 rounded-full bg-yellow-200 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-200">
                          +{achievement.perk.value} {achievement.perk.type.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {achievement.description}
                    </p>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                      Unlocked {new Date(achievement.unlockedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Locked Achievements (In Progress) */}
        {filteredProgress.length > 0 && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              In Progress
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {filteredProgress.map((progress) => (
                <div
                  key={progress.id}
                  className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                    <svg
                      className="h-6 w-6 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                      />
                    </svg>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-gray-900 dark:text-gray-100">
                      {progress.name}
                    </p>
                    <AchievementProgressBar
                      current={progress.current}
                      threshold={progress.threshold}
                      className="mt-2"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Motivational message */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-center dark:border-gray-800 dark:bg-gray-900">
          <p className="text-gray-600 dark:text-gray-400">
            {lifetimeCompleted >= 100
              ? "You're a productivity powerhouse! Keep crushing it!"
              : lifetimeCompleted >= 25
              ? "Great progress! Keep the momentum going."
              : lifetimeCompleted >= 5
              ? "You've made a great start! Keep completing tasks to level up."
              : "Start completing tasks to unlock achievements!"}
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}
