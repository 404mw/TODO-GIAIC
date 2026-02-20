/**
 * T157 — jest-axe integration for CommandPalette
 * NFR-003: Axe DevTools reports zero violations
 */

import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { CommandPalette } from '@/components/ui/CommandPalette'
import { useTasks } from '@/lib/hooks/useTasks'
import { useNotes } from '@/lib/hooks/useNotes'
import { useAuth } from '@/lib/hooks/useAuth'
import { useCommandPaletteStore } from '@/lib/stores/useCommandPaletteStore'
import { useNewTaskModalStore } from '@/lib/stores/new-task-modal.store'

expect.extend(toHaveNoViolations)

jest.mock('@/lib/hooks/useTasks')
jest.mock('@/lib/hooks/useNotes')
jest.mock('@/lib/hooks/useAuth')
jest.mock('@/lib/stores/useCommandPaletteStore')
jest.mock('@/lib/stores/new-task-modal.store')
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  usePathname: jest.fn(() => '/dashboard'),
}))

describe('T157 — CommandPalette accessibility', () => {
  beforeEach(() => {
    ;(useTasks as jest.Mock).mockReturnValue({ data: null, isLoading: false })
    ;(useNotes as jest.Mock).mockReturnValue({ data: null, isLoading: false })
    ;(useAuth as jest.Mock).mockReturnValue({ isAuthenticated: true })
    ;(useCommandPaletteStore as jest.Mock).mockReturnValue({
      isOpen: true,
      close: jest.fn(),
      open: jest.fn(),
    })
    ;(useNewTaskModalStore as jest.Mock).mockReturnValue({ open: jest.fn() })
  })

  it('has no axe violations when open', async () => {
    const { container } = render(<CommandPalette />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
