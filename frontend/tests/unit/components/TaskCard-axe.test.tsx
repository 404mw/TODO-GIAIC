/**
 * T157 — jest-axe integration for TaskCard
 * NFR-003: Axe DevTools reports zero violations
 */

import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { TaskCard } from '@/components/tasks/TaskCard'
import { useSubtasks } from '@/lib/hooks/useSubtasks'
import { useToast } from '@/lib/hooks/useToast'
import { useFocusModeStore } from '@/lib/stores/focus-mode.store'
import { usePendingCompletionsStore } from '@/lib/stores/usePendingCompletionsStore'
import type { Task } from '@/lib/schemas/task.schema'

expect.extend(toHaveNoViolations)

jest.mock('@/lib/hooks/useSubtasks')
jest.mock('@/lib/hooks/useToast')
jest.mock('@/lib/stores/focus-mode.store')
jest.mock('@/lib/stores/usePendingCompletionsStore')
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  usePathname: jest.fn(() => '/dashboard/tasks'),
}))

const mockTask: Task = {
  id: 'task-1',
  user_id: 'user-1',
  template_id: null,
  title: 'Test task for accessibility',
  description: 'A description',
  priority: 'medium',
  due_date: null,
  estimated_duration: 30,
  focus_time_seconds: 0,
  completed: false,
  completed_at: null,
  completed_by: null,
  hidden: false,
  archived: false,
  subtask_count: 0,
  subtask_completed_count: 0,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  version: 1,
}

describe('T157 — TaskCard accessibility', () => {
  beforeEach(() => {
    ;(useSubtasks as jest.Mock).mockReturnValue({ data: null, isLoading: false })
    ;(useToast as jest.Mock).mockReturnValue({ toast: jest.fn() })
    ;(useFocusModeStore as jest.Mock).mockReturnValue({ activate: jest.fn() })
    ;(usePendingCompletionsStore as jest.Mock).mockReturnValue({
      togglePending: jest.fn(),
      hasPending: jest.fn(() => false),
    })
  })

  it('has no axe violations', async () => {
    const { container } = render(<TaskCard task={mockTask} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('has no axe violations when task is completed', async () => {
    const completedTask = { ...mockTask, completed: true }
    const { container } = render(<TaskCard task={completedTask} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('has no axe violations when task is pending completion', async () => {
    ;(usePendingCompletionsStore as jest.Mock).mockReturnValue({
      togglePending: jest.fn(),
      hasPending: jest.fn(() => true),
    })
    const { container } = render(<TaskCard task={mockTask} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
