'use client'

import { useState, useMemo } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useAchievements, useAchievementDefinitions } from '@/lib/hooks/useAchievements'
import { AchievementDetailModal } from '@/components/achievements/AchievementDetailModal'
import type { AchievementCategory } from '@/lib/schemas/common.schema'
import type { AchievementDefinition } from '@/lib/schemas/achievement.schema'
import { Search, Trophy, Lock, Star, Flame, Target, Eye, FileText } from 'lucide-react'

/**
 * Achievements page (US5 - FR-029 to FR-033)
 *
 * Displays user productivity metrics and achievements:
 * - All achievements (locked and unlocked)
 * - Filters by status and category
 * - Search functionality
 * - Achievement detail modal
 * - User stats: streak, tasks completed, etc.
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

interface AchievementCardProps {
  achievement: AchievementDefinition
  isUnlocked: boolean
  userProgress?: number
  onClick: () => void
}

function AchievementCard({ achievement, isUnlocked, userProgress = 0, onClick }: AchievementCardProps) {
  const getCategoryIcon = (category: AchievementCategory) => {
    switch (category) {
      case 'tasks':
        return <Target className="h-5 w-5" />
      case 'streaks':
        return <Flame className="h-5 w-5" />
      case 'focus':
        return <Eye className="h-5 w-5" />
      case 'notes':
        return <FileText className="h-5 w-5" />
    }
  }

  const getCategoryColor = (category: AchievementCategory) => {
    switch (category) {
      case 'tasks':
        return 'blue'
      case 'streaks':
        return 'orange'
      case 'focus':
        return 'purple'
      case 'notes':
        return 'green'
    }
  }

  const categoryColor = getCategoryColor(achievement.category)
  const progress = Math.min((userProgress / achievement.threshold) * 100, 100)

  const colorClasses = {
    blue: {
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      text: 'text-blue-600 dark:text-blue-400',
      border: 'border-blue-200 dark:border-blue-800',
      progress: 'bg-blue-500',
    },
    orange: {
      bg: 'bg-orange-100 dark:bg-orange-900/30',
      text: 'text-orange-600 dark:text-orange-400',
      border: 'border-orange-200 dark:border-orange-800',
      progress: 'bg-orange-500',
    },
    purple: {
      bg: 'bg-purple-100 dark:bg-purple-900/30',
      text: 'text-purple-600 dark:text-purple-400',
      border: 'border-purple-200 dark:border-purple-800',
      progress: 'bg-purple-500',
    },
    green: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      text: 'text-green-600 dark:text-green-400',
      border: 'border-green-200 dark:border-green-800',
      progress: 'bg-green-500',
    },
  }

  const colors = colorClasses[categoryColor]

  return (
    <button
      onClick={onClick}
      className={`group relative w-full rounded-lg border ${
        isUnlocked
          ? `${colors.border} bg-white dark:bg-gray-900`
          : 'border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50'
      } p-6 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${
        !isUnlocked && 'opacity-60'
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-lg ${
            isUnlocked ? colors.bg : 'bg-gray-200 dark:bg-gray-800'
          } ${isUnlocked ? colors.text : 'text-gray-400 dark:text-gray-600'}`}
        >
          {isUnlocked ? (
            <Trophy className="h-6 w-6" />
          ) : (
            <Lock className="h-6 w-6" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {achievement.name}
            </h3>
            <div className={`flex items-center gap-1 text-xs ${colors.text}`}>
              {getCategoryIcon(achievement.category)}
              <span className="capitalize">{achievement.category}</span>
            </div>
          </div>

          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
            {achievement.message}
          </p>

          {/* Progress Bar for Locked Achievements */}
          {!isUnlocked && userProgress > 0 && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                <span>
                  {userProgress} / {achievement.threshold}
                </span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${colors.progress} transition-all duration-500`}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Perk Badge */}
          {achievement.perk_type && achievement.perk_value && (
            <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs font-medium">
              <Star className="h-3 w-3" />
              <span>
                +{achievement.perk_value}{' '}
                {achievement.perk_type.replace('_', ' ')}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Unlocked Badge */}
      {isUnlocked && (
        <div className="absolute top-3 right-3">
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs font-medium">
            <Trophy className="h-3 w-3" />
            <span>Unlocked</span>
          </div>
        </div>
      )}
    </button>
  )
}

type FilterStatus = 'all' | 'unlocked' | 'locked'

export default function AchievementsPage() {
  const { data: userStateResponse, isLoading: isLoadingUser, error: userError } = useAchievements()
  const { data: definitionsResponse, isLoading: isLoadingDefs, error: defsError } = useAchievementDefinitions()

  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all')
  const [filterCategory, setFilterCategory] = useState<AchievementCategory | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAchievement, setSelectedAchievement] = useState<AchievementDefinition | null>(null)

  const isLoading = isLoadingUser || isLoadingDefs
  const error = userError || defsError

  // Extract data
  const userState = userStateResponse?.data
  const definitions = definitionsResponse?.data || []
  const unlockedIds = userState?.unlocked_achievements || []

  // Calculate progress for each achievement
  const getProgress = (achievement: AchievementDefinition): number => {
    if (!userState) return 0

    switch (achievement.category) {
      case 'tasks':
        return userState.lifetime_tasks_completed
      case 'streaks':
        return userState.longest_streak
      case 'focus':
        return userState.focus_completions
      case 'notes':
        return userState.notes_converted
      default:
        return 0
    }
  }

  // Filter and search achievements
  const filteredAchievements = useMemo(() => {
    let filtered = definitions

    // Filter by status
    if (filterStatus === 'unlocked') {
      filtered = filtered.filter((a) => unlockedIds.includes(a.id))
    } else if (filterStatus === 'locked') {
      filtered = filtered.filter((a) => !unlockedIds.includes(a.id))
    }

    // Filter by category
    if (filterCategory !== 'all') {
      filtered = filtered.filter((a) => a.category === filterCategory)
    }

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (a) =>
          a.name.toLowerCase().includes(query) ||
          a.message.toLowerCase().includes(query)
      )
    }

    return filtered
  }, [definitions, unlockedIds, filterStatus, filterCategory, searchQuery])

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-purple-600" />
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

  // Stats
  const totalAchievements = definitions.length
  const unlockedCount = unlockedIds.length
  const streak = {
    currentStreak: userState?.current_streak || 0,
    longestStreak: userState?.longest_streak || 0,
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Achievements
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Track your productivity and unlock rewards
          </p>
        </div>

        {/* Stats Overview */}
        <div className="rounded-xl border border-purple-200 dark:border-purple-900/50 bg-linear-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Your Progress
              </h2>
              <p className="text-4xl font-bold text-purple-600 dark:text-purple-400 mt-1">
                {unlockedCount} / {totalAchievements}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                achievements unlocked
              </p>
            </div>
            <div className="flex items-center justify-center h-24 w-24 rounded-full bg-purple-100 dark:bg-purple-900/50">
              <Trophy className="h-12 w-12 text-purple-600 dark:text-purple-400" />
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-linear-to-r from-purple-500 to-blue-500 transition-all duration-500"
                style={{
                  width: `${totalAchievements > 0 ? (unlockedCount / totalAchievements) * 100 : 0}%`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            title="Tasks Completed"
            value={userState?.lifetime_tasks_completed || 0}
            subtitle="All-time total"
            color="blue"
            icon={<Target className="h-6 w-6" />}
          />

          <MetricCard
            title="Current Streak"
            value={`${streak.currentStreak} days`}
            subtitle={`Best: ${streak.longestStreak} days`}
            color="orange"
            icon={<Flame className="h-6 w-6" />}
          />

          <MetricCard
            title="Focus Sessions"
            value={userState?.focus_completions || 0}
            subtitle="Deep work completed"
            color="purple"
            icon={<Eye className="h-6 w-6" />}
          />
        </div>

        {/* Filters and Search */}
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search achievements..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-600 focus:border-transparent"
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex flex-wrap gap-3">
            {/* Status Filters */}
            <div className="flex items-center gap-2">
              {(['all', 'unlocked', 'locked'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filterStatus === status
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>

            <div className="h-8 w-px bg-gray-300 dark:bg-gray-700" />

            {/* Category Filters */}
            <div className="flex items-center gap-2 flex-wrap">
              {(['all', 'tasks', 'streaks', 'focus', 'notes'] as const).map((category) => (
                <button
                  key={category}
                  onClick={() => setFilterCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                    filterCategory === category
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Achievements Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {filterStatus === 'all'
                ? 'All Achievements'
                : filterStatus === 'unlocked'
                ? 'Unlocked Achievements'
                : 'Locked Achievements'}
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {filteredAchievements.length} {filteredAchievements.length === 1 ? 'achievement' : 'achievements'}
            </span>
          </div>

          {filteredAchievements.length === 0 ? (
            <div className="text-center py-12 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
              <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">
                {searchQuery
                  ? 'No achievements match your search'
                  : 'No achievements found'}
              </p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {filteredAchievements.map((achievement) => (
                <AchievementCard
                  key={achievement.id}
                  achievement={achievement}
                  isUnlocked={unlockedIds.includes(achievement.id)}
                  userProgress={getProgress(achievement)}
                  onClick={() => setSelectedAchievement(achievement)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Achievement Detail Modal */}
        {selectedAchievement && (
          <AchievementDetailModal
            achievement={selectedAchievement}
            isUnlocked={unlockedIds.includes(selectedAchievement.id)}
            userProgress={getProgress(selectedAchievement)}
            onClose={() => setSelectedAchievement(null)}
          />
        )}
      </div>
    </DashboardLayout>
  )
}
