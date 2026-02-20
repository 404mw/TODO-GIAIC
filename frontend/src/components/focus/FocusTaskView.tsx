'use client'

import { useEffect } from 'react'
import { useFocusModeStore } from '@/lib/stores/focus-mode.store'

/**
 * FocusTaskView — Navigation guard component for focus mode (T172 / FR-004)
 *
 * When focus mode is active, this component registers:
 * 1. A popstate (browser Back) listener that shows window.confirm before
 *    allowing navigation away from the focus session.
 * 2. A beforeunload listener that prompts the user before closing the tab.
 *
 * Must be rendered inside the focus mode page while isActive is true.
 * Returns null — it only manages side-effects.
 */
export function FocusTaskView() {
  const { isActive, deactivate } = useFocusModeStore()

  useEffect(() => {
    if (!isActive) return

    const handlePopState = () => {
      const leave = window.confirm('Exit focus mode? Your progress will be saved.')
      if (leave) {
        deactivate()
      } else {
        // Push the state back so the browser doesn't actually navigate
        window.history.pushState(null, '', window.location.href)
      }
    }

    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault()
      event.returnValue = 'Exit focus mode? Your progress will be saved.'
      return event.returnValue
    }

    // Push a state so we can intercept the first Back press
    window.history.pushState(null, '', window.location.href)

    window.addEventListener('popstate', handlePopState)
    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('popstate', handlePopState)
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [isActive, deactivate])

  return null
}
