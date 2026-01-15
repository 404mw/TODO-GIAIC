'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useSidebarStore } from '@/lib/stores/useSidebarStore'
import { useNewTaskModalStore } from '@/lib/stores/useNewTaskModalStore'
import { NotificationDropdown } from '@/components/layout/NotificationDropdown'
import { navigationItems } from '@/lib/config/navigation'

/**
 * Header/Top bar component
 *
 * Features:
 * - Hamburger menu (mobile)
 * - Logo (mobile)
 * - New Task/Note dropdown
 * - Quick notification access
 */

export function Header() {
  const { isOpen: isSidebarOpen, toggle: toggleSidebar } = useSidebarStore()
  const openNewTaskModal = useNewTaskModalStore((state) => state.open)
  const [showNewDropdown, setShowNewDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const pathname = usePathname()

  // Find active navigation item for page title
  const activeNavItem = navigationItems.find((item) => {
    if (item.href === '/dashboard') {
      return pathname === '/dashboard'
    }
    return pathname.startsWith(item.href)
  })
  const pageTitle = activeNavItem?.label || 'Dashboard'

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNewDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleNewTask = () => {
    setShowNewDropdown(false)
    openNewTaskModal()
  }

  const handleNewNote = () => {
    setShowNewDropdown(false)
    // TODO: Open new note modal when implemented
    console.log('New note clicked')
  }

  return (
    <header className="sticky top-0 z-30 h-16 border-b border-gray-200 bg-white/80 backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/80">
      <div className="flex h-full items-center justify-between px-4 lg:px-6">
        {/* Left: Hamburger menu and Logo (mobile only) */}
        <div className="flex items-center gap-3 lg:hidden">
          <button
            onClick={toggleSidebar}
            className="rounded-md p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label={isSidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {isSidebarOpen ? (
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
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
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            )}
          </button>
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <span className="text-lg font-bold text-white">P</span>
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Perpetua
            </span>
          </Link>
        </div>

        {/* Page title for desktop */}
        <div className="hidden lg:flex lg:flex-1 lg:items-center">
          <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {pageTitle}
          </h1>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {/* Credits info button */}
          <button
            className="flex items-center gap-1.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="Credits info"
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
            <span className="hidden sm:inline">Credits</span>
          </button>

          {/* New Task/Note dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowNewDropdown(!showNewDropdown)}
              className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              aria-label="Create new"
              data-onboarding="new-task-button"
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <span className="hidden sm:inline">New</span>
              <svg
                className={`h-4 w-4 transition-transform ${showNewDropdown ? 'rotate-180' : ''}`}
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

            {/* Dropdown menu */}
            {showNewDropdown && (
              <div className="absolute right-0 mt-2 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800">
                <button
                  onClick={handleNewTask}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
                >
                  <svg
                    className="h-4 w-4 text-blue-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                    />
                  </svg>
                  New Task
                </button>
                <button
                  onClick={handleNewNote}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
                >
                  <svg
                    className="h-4 w-4 text-purple-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  New Note
                </button>
              </div>
            )}
          </div>

          {/* Notifications */}
          <NotificationDropdown />
        </div>
      </div>
    </header>
  )
}
