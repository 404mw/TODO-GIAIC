/**
 * OnboardingTour Component (T143-T147)
 * Phase 11 - US7 Onboarding
 *
 * Interactive walkthrough using Driver.js to guide new users
 * through the application features.
 *
 * Features:
 * - Auto-starts on first login if user hasn't seen onboarding
 * - Can be replayed from Settings page
 * - Dark-themed styling to match app aesthetic
 */

'use client'

import { useEffect, useCallback, useRef } from 'react'
import { driver, DriveStep, Config } from 'driver.js'
import 'driver.js/dist/driver.css'

export interface OnboardingTourProps {
  /** Start the tour automatically */
  autoStart?: boolean
  /** Called when tour is completed or dismissed */
  onComplete?: () => void
  /** Called when tour is skipped */
  onSkip?: () => void
}

// Storage key for tracking onboarding status
const ONBOARDING_COMPLETED_KEY = 'perpetua-onboarding-completed'

// Check if onboarding has been completed
export function hasCompletedOnboarding(): boolean {
  if (typeof window === 'undefined') return true
  return localStorage.getItem(ONBOARDING_COMPLETED_KEY) === 'true'
}

// Mark onboarding as completed
export function markOnboardingComplete(): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(ONBOARDING_COMPLETED_KEY, 'true')
}

// Reset onboarding status (for replay from Settings)
export function resetOnboarding(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(ONBOARDING_COMPLETED_KEY)
}

// Tour steps configuration
const getTourSteps = (): DriveStep[] => [
  {
    element: '[data-onboarding="sidebar"]',
    popover: {
      title: 'Navigation Sidebar',
      description: 'Access all your productivity tools from here. Navigate between Tasks, Notes, Focus Mode, and Achievements.',
      side: 'right',
      align: 'start',
    },
  },
  {
    element: '[data-onboarding="tasks-link"]',
    popover: {
      title: 'Tasks',
      description: 'Manage all your tasks here. Create, organize, and track your to-dos with priorities and due dates.',
      side: 'right',
      align: 'center',
    },
  },
  {
    element: '[data-onboarding="new-task-button"]',
    popover: {
      title: 'Create New Task',
      description: 'Click here to add a new task. You can set priorities, due dates, and even add sub-tasks!',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-onboarding="focus-link"]',
    popover: {
      title: 'Focus Mode',
      description: 'Eliminate distractions and concentrate on one task at a time with our built-in timer.',
      side: 'right',
      align: 'center',
    },
  },
  {
    element: '[data-onboarding="notes-link"]',
    popover: {
      title: 'Quick Notes',
      description: 'Capture thoughts and ideas instantly. You can even convert notes into tasks later!',
      side: 'right',
      align: 'center',
    },
  },
  {
    element: '[data-onboarding="achievements-link"]',
    popover: {
      title: 'Achievements',
      description: 'Track your productivity streaks, celebrate milestones, and stay motivated!',
      side: 'right',
      align: 'center',
    },
  },
  {
    element: '[data-onboarding="search-button"]',
    popover: {
      title: 'Global Search',
      description: 'Press Cmd+K (or Ctrl+K) anytime to quickly search tasks, notes, or navigate anywhere.',
      side: 'bottom',
      align: 'center',
    },
  },
  {
    element: '[data-onboarding="profile"]',
    popover: {
      title: 'Profile & Settings',
      description: 'Access your profile settings and customize the app to your preferences.',
      side: 'left',
      align: 'end',
    },
  },
]

export function OnboardingTour({
  autoStart = false,
  onComplete,
  onSkip,
}: OnboardingTourProps) {
  const driverRef = useRef<ReturnType<typeof driver> | null>(null)
  const hasStarted = useRef(false)

  const startTour = useCallback(() => {
    if (hasStarted.current) return
    hasStarted.current = true

    const driverConfig: Config = {
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: getTourSteps(),
      nextBtnText: 'Next',
      prevBtnText: 'Back',
      doneBtnText: 'Done',
      progressText: '{{current}} of {{total}}',
      onDestroyStarted: () => {
        // Called when tour is completed or dismissed
        markOnboardingComplete()
        onComplete?.()
        hasStarted.current = false
      },
      onCloseClick: () => {
        // Called when close button is clicked (skipped)
        markOnboardingComplete()
        onSkip?.()
        hasStarted.current = false
        driverRef.current?.destroy()
      },
      // Custom styling for dark theme
      popoverClass: 'perpetua-tour-popover',
      overlayColor: 'rgba(0, 0, 0, 0.7)',
    }

    driverRef.current = driver(driverConfig)
    driverRef.current.drive()
  }, [onComplete, onSkip])

  useEffect(() => {
    if (autoStart && !hasCompletedOnboarding()) {
      // Slight delay to ensure DOM elements are rendered
      const timer = setTimeout(startTour, 500)
      return () => clearTimeout(timer)
    }
  }, [autoStart, startTour])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (driverRef.current) {
        driverRef.current.destroy()
      }
    }
  }, [])

  return null // This component only manages the tour, no visible UI
}

// Export a hook to start the tour manually
export function useOnboardingTour() {
  const startTour = useCallback((onComplete?: () => void) => {
    const driverConfig: Config = {
      showProgress: true,
      showButtons: ['next', 'previous', 'close'],
      steps: getTourSteps(),
      nextBtnText: 'Next',
      prevBtnText: 'Back',
      doneBtnText: 'Done',
      progressText: '{{current}} of {{total}}',
      onDestroyStarted: () => {
        onComplete?.()
      },
      popoverClass: 'perpetua-tour-popover',
      overlayColor: 'rgba(0, 0, 0, 0.7)',
    }

    const driverInstance = driver(driverConfig)
    driverInstance.drive()
    return driverInstance
  }, [])

  return { startTour, hasCompletedOnboarding, resetOnboarding }
}
