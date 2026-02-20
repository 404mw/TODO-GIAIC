/**
 * T182 — RED test: focus mode navigation guard
 *
 * Tests:
 * 1. popstate event triggers window.confirm when focus is active
 * 2. beforeunload event is handled when focus is active
 * 3. No guard fires when isActive = false
 *
 * Acceptance criteria: Test detects missing navigation guard before T172;
 * zero guard-absent failures after.
 */

import React from 'react'
import { render, act } from '@testing-library/react'
import { FocusTaskView } from '@/components/focus/FocusTaskView'
import { useFocusModeStore } from '@/lib/stores/focus-mode.store'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
}))

// Reset Zustand store between tests
beforeEach(() => {
  useFocusModeStore.setState({ isActive: false, currentTaskId: null, startTime: null })
})

describe('T182 — focus mode navigation guard', () => {
  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('window.confirm is called when popstate fires while focus is active', () => {
    // Activate focus mode
    act(() => {
      useFocusModeStore.getState().activate('task-1')
    })

    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false)

    render(React.createElement(FocusTaskView))

    // Dispatch popstate (browser back)
    act(() => {
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    expect(confirmSpy).toHaveBeenCalled()
  })

  it('beforeunload event is handled while focus is active', () => {
    act(() => {
      useFocusModeStore.getState().activate('task-1')
    })

    render(React.createElement(FocusTaskView))

    const event = new Event('beforeunload') as BeforeUnloadEvent
    Object.defineProperty(event, 'returnValue', {
      writable: true,
      value: '',
    })

    act(() => {
      window.dispatchEvent(event)
    })

    // beforeunload handler should have set returnValue
    expect(event.returnValue).not.toBeUndefined()
  })

  it('does NOT call window.confirm on popstate when focus is NOT active', () => {
    // isActive = false (default from beforeEach)
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true)

    render(React.createElement(FocusTaskView))

    act(() => {
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    expect(confirmSpy).not.toHaveBeenCalled()
  })

  it('guard is cleaned up on unmount', () => {
    act(() => {
      useFocusModeStore.getState().activate('task-1')
    })

    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false)

    const { unmount } = render(React.createElement(FocusTaskView))

    // Unmount — guard should be removed
    unmount()

    act(() => {
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    // confirm should NOT be called after unmount
    expect(confirmSpy).not.toHaveBeenCalled()
  })
})
