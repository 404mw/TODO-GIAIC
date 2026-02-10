'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { useSidebarStore } from '@/lib/stores/useSidebarStore'
import { useFocusStore } from '@/lib/stores/useFocusStore'
import { useCommandPaletteStore } from '@/lib/stores/useCommandPaletteStore'
import { NavigationMenu } from '@/components/layout/NavigationMenu'
import { ProfilePopover } from '@/components/layout/ProfilePopover'
import { navigationItems } from '@/lib/config/navigation'

/**
 * Sidebar navigation component
 *
 * Features:
 * - Collapsible sidebar with persistent state (icons-only when collapsed)
 * - Active route highlighting via NavigationMenu
 * - Global search input
 * - Focus Mode integration (hides sidebar when active)
 * - Full ARIA labels and semantic HTML for accessibility
 * - Smooth animations with prefers-reduced-motion support
 * - Flap button on collapsed sidebar edge to expand
 * - Logo hover effect to show expand arrow when collapsed
 *
 * FR-035: Collapsible sidebar
 * FR-036: Persistent sidebar state
 * FR-039: Focus Mode hides sidebar
 * FR-052: Smooth animations
 * FR-054: Reduced motion support
 * T063: Extracted navigation config
 * T064: Enhanced accessibility
 * T065: Framer Motion animations
 */

export function Sidebar() {
  const { isOpen, isMobile, toggle, close, setMobile } = useSidebarStore()
  const { isActive: isFocusModeActive } = useFocusStore()
  const { open: openCommandPalette } = useCommandPaletteStore()
  const [isLogoHovered, setIsLogoHovered] = useState(false)

  // Handle window resize to detect mobile/desktop
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024
      setMobile(mobile)
    }

    // Set initial state
    handleResize()

    // Listen for resize
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [setMobile])

  // Handle swipe to close on mobile
  const handleDragEnd = (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    // Only on mobile and when sidebar is open
    if (isMobile && isOpen) {
      // If dragged left more than 50px or velocity is negative, close
      if (info.offset.x < -50 || info.velocity.x < -500) {
        close()
      }
    }
  }

  // FR-039: Hide sidebar when Focus Mode is active
  if (isFocusModeActive) {
    return null
  }

  return (
    <>
      {/* Sidebar */}
      <motion.aside
        role="complementary"
        aria-label="Main navigation sidebar"
        data-onboarding="sidebar"
        initial={false}
        animate={
          isMobile
            ? {
                // Mobile: slide in/out
                x: isOpen ? 0 : -256,
                width: 256,
              }
            : {
                // Desktop: collapse/expand width
                x: 0,
                width: isOpen ? 256 : 72,
              }
        }
        drag={isMobile && isOpen ? 'x' : false}
        dragConstraints={{ left: -256, right: 0 }}
        dragElastic={0.1}
        onDragEnd={handleDragEnd}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 30,
        }}
        className={[
          'fixed left-0 top-0 z-40 h-screen',
          'bg-white dark:bg-gray-900',
          'border-r border-gray-200 dark:border-gray-800',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {/* Sidebar flap button - desktop only (mobile uses header hamburger) */}
        <button
          onClick={toggle}
          className="absolute -right-3 top-1/2 -translate-y-1/2 z-60 hidden lg:flex h-6 w-6 items-center justify-center rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-md text-gray-500 hover:text-blue-600 hover:border-blue-300 dark:hover:text-blue-400 dark:hover:border-blue-600 transition-colors"
          aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          <svg
            className={`h-3.5 w-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>

        <div className="flex h-full flex-col">
          {/* Header */}
          <div className={`flex h-16 items-center ${isOpen ? 'px-4 justify-between' : 'justify-center px-2'} border-b border-gray-200 dark:border-gray-800`}>
            {isOpen ? (
              <Link
                href="/dashboard"
                className="flex items-center gap-2"
                aria-label="Perpetua home"
              >
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 shrink-0"
                  aria-hidden="true"
                >
                  <span className="text-lg font-bold text-white">P</span>
                </div>
                <motion.span
                  initial={false}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.1, duration: 0.15 }}
                  className="text-xl font-bold text-gray-900 dark:text-gray-100"
                >
                  Perpetua
                </motion.span>
              </Link>
            ) : (
              <button
                onClick={toggle}
                onMouseEnter={() => setIsLogoHovered(true)}
                onMouseLeave={() => setIsLogoHovered(false)}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 shrink-0 transition-all hover:bg-blue-700"
                aria-label="Expand sidebar"
              >
                <AnimatePresence mode="wait">
                  {isLogoHovered ? (
                    <motion.svg
                      key="arrow"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.15 }}
                      className="h-4 w-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2.5}
                        d="M9 5l7 7-7 7"
                      />
                    </motion.svg>
                  ) : (
                    <motion.span
                      key="letter"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ duration: 0.15 }}
                      className="text-lg font-bold text-white"
                    >
                      P
                    </motion.span>
                  )}
                </AnimatePresence>
              </button>
            )}
          </div>

          {/* Global Search */}
          {isOpen ? (
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800" data-onboarding="search-button">
              <button
                onClick={openCommandPalette}
                className="flex w-full items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-500 dark:text-gray-400 hover:border-gray-400 dark:hover:border-gray-600 transition-colors"
                aria-label="Open search"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <span className="flex-1 text-left">Search...</span>
                <kbd className="hidden sm:inline-block rounded border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-1.5 py-0.5 text-xs font-medium text-gray-500 dark:text-gray-400">
                  ⌘K
                </kbd>
              </button>
            </div>
          ) : (
            <div className="flex justify-center py-3 border-b border-gray-200 dark:border-gray-800">
              <button
                onClick={openCommandPalette}
                className="rounded-md p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Search"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </button>
            </div>
          )}

          {/* Navigation */}
          <NavigationMenu items={navigationItems} collapsed={!isOpen} />

          {/* Profile Popover - at bottom */}
          <div className={`mt-auto border-t border-gray-200 dark:border-gray-800 ${isOpen ? 'p-3' : 'py-3 flex justify-center'}`} data-onboarding="profile">
            <ProfilePopover collapsed={!isOpen} />
          </div>
        </div>
      </motion.aside>

      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={toggle}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>
    </>
  )
}
