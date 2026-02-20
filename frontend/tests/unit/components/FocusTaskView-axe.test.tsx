/**
 * T157 — jest-axe integration for FocusTimer (FocusTaskView scope)
 * NFR-003: Axe DevTools reports zero violations
 */

import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { FocusTimer } from '@/components/focus/FocusTimer'

expect.extend(toHaveNoViolations)

describe('T157 — FocusTimer (FocusTaskView) accessibility', () => {
  it('has no axe violations in running state', async () => {
    const { container } = render(
      <FocusTimer
        durationMinutes={25}
        onComplete={jest.fn()}
        onPause={jest.fn()}
        onResume={jest.fn()}
        onExit={jest.fn()}
        isRunning={true}
      />
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('has no axe violations in paused state', async () => {
    const { container } = render(
      <FocusTimer
        durationMinutes={25}
        onComplete={jest.fn()}
        onPause={jest.fn()}
        onResume={jest.fn()}
        onExit={jest.fn()}
        isRunning={false}
      />
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
