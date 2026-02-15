'use client'

import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/lib/hooks/useAuth'
import { useAchievements, useAchievementDefinitions } from '@/lib/hooks/useAchievements'
import { Trophy, ExternalLink, Lock } from 'lucide-react'
import type { AchievementDefinition } from '@/lib/schemas/achievement.schema'

/**
 * User Profile Page
 *
 * Displays user information and account settings:
 * - Name and avatar
 * - Email (read-only)
 * - Subscription plan and status
 * - Recent achievements
 * - Upgrade to Pro CTA (if on free plan)
 */

export default function ProfilePage() {
  const { user } = useAuth()
  const { data: userStateResponse } = useAchievements()
  const { data: definitionsResponse } = useAchievementDefinitions()

  const unlockedIds = userStateResponse?.data?.unlocked || []
  const definitions = definitionsResponse?.data || []

  // Get unlocked achievement details
  const unlockedAchievements = definitions.filter((def) =>
    unlockedIds.includes(def.id)
  )

  // Show top 5 most recent achievements (for demo, just show first 5)
  const recentAchievements = unlockedAchievements.slice(0, 5)

  const userName = user?.name || 'User'
  const userEmail = user?.email || ''
  const userPlan = user?.tier || 'free'

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Profile
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Manage your account information and preferences
          </p>
        </div>

        {/* Profile Information Card */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-6 text-lg font-semibold text-gray-900 dark:text-gray-100">
            Account Information
          </h2>

          <div className="space-y-6">
            {/* Avatar */}
            <div className="flex items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-600 text-white text-2xl font-bold">
                {userName.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Profile Photo
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Avatar customization coming soon
                </p>
              </div>
            </div>

            {/* Name */}
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Name
              </label>
              <input
                id="name"
                type="text"
                value={userName}
                readOnly
                className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 cursor-not-allowed"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Name editing coming soon
              </p>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                value={userEmail}
                readOnly
                className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 cursor-not-allowed"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Email address cannot be changed
              </p>
            </div>
          </div>
        </div>

        {/* Achievements Card */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Recent Achievements
            </h2>
            <Link
              href="/dashboard/achievements"
              className="flex items-center gap-1 text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors"
            >
              View All
              <ExternalLink className="h-4 w-4" />
            </Link>
          </div>

          {recentAchievements.length === 0 ? (
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 mb-3">
                <Lock className="h-6 w-6 text-gray-400" />
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                No achievements unlocked yet
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Start completing tasks to earn your first achievement!
              </p>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {recentAchievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className="flex items-center gap-3 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 p-4"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                    <Trophy className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                      {achievement.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
                      {achievement.message}
                    </p>
                    {achievement.perk_type && achievement.perk_value && (
                      <div className="mt-1 flex items-center gap-1 text-xs text-purple-600 dark:text-purple-400">
                        <span className="font-medium">
                          +{achievement.perk_value} {achievement.perk_type.replace('_', ' ')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Stats Summary */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                Total achievements unlocked
              </span>
              <span className="font-bold text-purple-600 dark:text-purple-400">
                {unlockedIds.length} / {definitions.length}
              </span>
            </div>
          </div>
        </div>

        {/* Subscription Card */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
            Subscription
          </h2>

          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Current Plan:
                </p>
                <span
                  className={[
                    'rounded-full px-3 py-1 text-xs font-semibold',
                    userPlan === 'pro'
                      ? 'bg-linear-to-r from-blue-500 to-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
                  ].join(' ')}
                >
                  {userPlan === 'pro' ? '✨ Pro' : 'Free'}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {userPlan === 'pro'
                  ? 'You have access to all premium features'
                  : 'Upgrade to Pro for unlimited tasks, AI features, and more'}
              </p>
            </div>

            {userPlan === 'free' && (
              <Link href="/pricing">
                <Button>Upgrade to Pro</Button>
              </Link>
            )}
          </div>

          {userPlan === 'pro' && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">
                  Next billing date
                </span>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  Coming soon
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Account Actions */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
            Account Actions
          </h2>

          <div className="space-y-3">
            <Link
              href="/dashboard/settings"
              className="flex items-center justify-between rounded-lg border border-gray-200 p-4 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center gap-3">
                <svg
                  className="h-5 w-5 text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    Settings
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Manage app preferences
                  </p>
                </div>
              </div>
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Link>

            <Link
              href="/dashboard/credits"
              className="flex items-center justify-between rounded-lg border border-gray-200 p-4 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center gap-3">
                <svg
                  className="h-5 w-5 text-yellow-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    Credits
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    View and manage your credits
                  </p>
                </div>
              </div>
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
