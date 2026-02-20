/**
 * T157 — jest-axe integration for NewTaskModal
 * NFR-003: Axe DevTools reports zero violations
 */

import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { NewTaskModal } from '@/components/tasks/NewTaskModal'
import { useCreateTask, useUpdateTask } from '@/lib/hooks/useTasks'
import { useToast } from '@/lib/hooks/useToast'

expect.extend(toHaveNoViolations)

jest.mock('@/lib/hooks/useTasks')
jest.mock('@/lib/hooks/useToast')
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  usePathname: jest.fn(() => '/dashboard/tasks'),
}))

describe('T157 — NewTaskModal accessibility', () => {
  beforeEach(() => {
    ;(useCreateTask as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn(),
      isPending: false,
    })
    ;(useUpdateTask as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn(),
      isPending: false,
    })
    ;(useToast as jest.Mock).mockReturnValue({ toast: jest.fn() })
  })

  it('has no axe violations when open', async () => {
    const { container } = render(
      <NewTaskModal open={true} onOpenChange={jest.fn()} />
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
