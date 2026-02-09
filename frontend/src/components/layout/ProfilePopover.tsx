'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/Popover'
import { useAuth } from '@/lib/hooks/useAuth'
import { useSubscription } from '@/lib/hooks/useSubscription'

/**
 * ProfilePopover Component
 *
 * Features:
 * - User profile information display
 * - Quick links to settings
 * - Logout functionality
 *
 * FR-037: User profile display
 * FR-038: Settings access
 */

interface ProfilePopoverProps {
  collapsed?: boolean
}

export function ProfilePopover({
  collapsed = false,
}: ProfilePopoverProps) {
  const router = useRouter()
  const { user, logout } = useAuth()
  const { data: subscriptionData } = useSubscription()

  const userName = user?.name || 'User'
  const userTier = user?.tier || 'free'
  const planDisplay = userTier === 'pro' ? '✨ Pro' : 'Free Plan'

  const handleLogout = async () => {
    try {
      logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          className={`flex items-center rounded-lg text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors ${
            collapsed ? 'p-2 justify-center' : 'gap-3 w-full px-3 py-2'
          }`}
          aria-label="User profile menu"
          title={collapsed ? userName : undefined}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white font-semibold text-sm shrink-0">
            {userName.charAt(0).toUpperCase()}
          </div>
          {!collapsed && (
            <div className="flex flex-col items-start">
              <span className="font-medium">{userName}</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {planDisplay}
              </span>
            </div>
          )}
        </button>
      </PopoverTrigger>

      <PopoverContent align="end" className="w-64">
        <div className="space-y-4">
          {/* User Info */}
          <div className="pb-3 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
                {userName.charAt(0).toUpperCase()}
              </div>
              <div className="flex flex-col">
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {userName}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {planDisplay}
                </span>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div className="space-y-1">
            <Link
              href="/dashboard/profile"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors"
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
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              View Profile
            </Link>

            <Link
              href="/dashboard/credits"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors"
            >
              <svg
                className="h-4 w-4 text-yellow-500"
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
              Credits
            </Link>

            <Link
              href="/dashboard/settings"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors"
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
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              Settings
            </Link>

            <Link
              href="/contact"
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors"
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
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Help & Support
            </Link>
          </div>

          {/* Logout */}
          <div className="pt-3 border-t border-gray-200 dark:border-gray-800">
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/20 transition-colors"
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
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Log Out
            </button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
