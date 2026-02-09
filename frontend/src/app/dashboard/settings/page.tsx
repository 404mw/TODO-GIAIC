'use client'

import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useOnboardingTour, resetOnboarding } from '@/components/onboarding/OnboardingTour'

/**
 * Settings page
 *
 * Main settings hub with navigation to specific settings sections.
 * Features:
 * - Hidden tasks management
 * - Preferences (coming soon)
 * - Onboarding replay
 */

interface SettingsSection {
  title: string
  message: string
  href: string
  icon: React.ReactNode
  disabled?: boolean
}

const settingsSections: SettingsSection[] = [
  {
    title: 'Hidden Tasks',
    message: 'View and manage tasks you have hidden from the main view',
    href: '/dashboard/settings/hidden-tasks',
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
        />
      </svg>
    ),
  },
  {
    title: 'Archived Notes',
    message: 'View and manage notes you have archived',
    href: '/dashboard/settings/archived-notes',
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
        />
      </svg>
    ),
  },
  {
    title: 'Preferences',
    message: 'Customize your app experience and defaults',
    href: '#',
    disabled: true,
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
    ),
  },
]

export default function SettingsPage() {
  const router = useRouter()
  const { startTour } = useOnboardingTour()

  const handleReplayOnboarding = () => {
    resetOnboarding()
    router.push('/dashboard')
    // Start tour after a brief delay to allow navigation
    setTimeout(() => {
      startTour()
    }, 500)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Settings
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Manage your preferences and account settings
          </p>
        </div>

        {/* Settings Sections */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {settingsSections.map((section) => {
            const cardContent = (
              <div className="flex items-start gap-4">
                <div
                  className={[
                    'flex h-12 w-12 shrink-0 items-center justify-center rounded-lg transition-colors',
                    section.disabled
                      ? 'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600'
                      : 'bg-gray-100 text-gray-600 group-hover:bg-blue-50 group-hover:text-blue-600 dark:bg-gray-800 dark:text-gray-400 dark:group-hover:bg-blue-900/20 dark:group-hover:text-blue-400',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                >
                  {section.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    {section.title}
                    {section.disabled && (
                      <span className="ml-2 text-xs font-normal text-gray-500">
                        (Coming soon)
                      </span>
                    )}
                  </h3>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {section.message}
                  </p>
                </div>
                {!section.disabled && (
                  <svg
                    className="h-5 w-5 shrink-0 text-gray-400 transition-transform group-hover:translate-x-1 group-hover:text-blue-500"
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
                )}
              </div>
            )

            if (section.disabled) {
              return (
                <div
                  key={section.href}
                  title="Coming soon"
                  className="group rounded-lg border border-gray-200 bg-white p-6 transition-all dark:border-gray-800 dark:bg-gray-900 cursor-not-allowed opacity-50"
                >
                  {cardContent}
                </div>
              )
            }

            return (
              <Link
                key={section.href}
                href={section.href}
                className="group rounded-lg border border-gray-200 bg-white p-6 transition-all dark:border-gray-800 dark:bg-gray-900 hover:border-blue-300 hover:shadow-md dark:hover:border-blue-700"
              >
                {cardContent}
              </Link>
            )
          })}

          {/* Replay Onboarding - Special action button */}
          <button
            onClick={handleReplayOnboarding}
            className="group rounded-lg border border-gray-200 bg-white p-6 text-left transition-all hover:border-blue-300 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:hover:border-blue-700"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-colors group-hover:bg-blue-50 group-hover:text-blue-600 dark:bg-gray-800 dark:text-gray-400 dark:group-hover:bg-blue-900/20 dark:group-hover:text-blue-400">
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Replay Onboarding
                </h3>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Start the guided walkthrough again
                </p>
              </div>
              <svg
                className="h-5 w-5 flex-shrink-0 text-gray-400 transition-transform group-hover:translate-x-1 group-hover:text-blue-500"
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
            </div>
          </button>
        </div>
      </div>
    </DashboardLayout>
  )
}
