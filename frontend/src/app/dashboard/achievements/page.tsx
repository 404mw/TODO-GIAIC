'use client'

import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useAchievements } from '@/lib/hooks/useAchievements'

/**
 * Achievements page (US5 - FR-029 to FR-033)
 *
 * Displays user productivity metrics and achievements:
 * - Consistency streak with grace day logic
 * - High-priority tasks completed (highPrioritySlays)
 * - Completion ratio
 * - Milestones unlocked
 */

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

  const streak = achievements?.consistencyStreak
  const highPrioritySlays = achievements?.highPrioritySlays || 0
  const completionRatio = achievements?.completionRatio || 0
  const milestones = achievements?.milestones || []

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Achievements
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Track your productivity and celebrate your wins
          </p>
        </div>

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
                {streak?.currentStreak || 0} days
              </p>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Longest streak: {streak?.longestStreak || 0} days
                {streak?.graceDayUsed && ' (grace day active)'}
              </p>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            title="High Priority Slays"
            value={highPrioritySlays}
            subtitle="Urgent tasks conquered"
            color="red"
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
            title="Completion Ratio"
            value={`${Math.round(completionRatio)}%`}
            subtitle="Tasks completed on time"
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
            title="Milestones Unlocked"
            value={milestones.length}
            subtitle="Achievements earned"
            color="purple"
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

        {/* Milestones List */}
        {milestones.length > 0 && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Earned Milestones
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {milestones.map((milestone) => (
                <div
                  key={milestone.id}
                  className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                    <svg
                      className="h-5 w-5 text-yellow-600 dark:text-yellow-400"
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
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {milestone.name}
                    </p>
                    <p className="truncate text-sm text-gray-500 dark:text-gray-400">
                      {milestone.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Motivational message */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-center dark:border-gray-800 dark:bg-gray-900">
          <p className="text-gray-600 dark:text-gray-400">
            {highPrioritySlays >= 50
              ? "You're a productivity powerhouse! Keep crushing it!"
              : highPrioritySlays >= 10
              ? "Great progress on high-priority tasks! Keep the momentum going."
              : highPrioritySlays >= 1
              ? "You've started slaying! Complete more high-priority tasks to level up."
              : "Start completing high-priority tasks to unlock achievements!"}
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}
