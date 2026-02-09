/**
 * T051 [P] [US8] Test: Sidebar renders nav links and search
 * T052 [P] [US8] Test: Sidebar collapse persists in localStorage (FR-036)
 */

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Sidebar } from '@/components/layout/Sidebar'
import { useSidebarStore } from '@/lib/stores/useSidebarStore'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/'),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
}))

describe('Sidebar Component - RED Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    // Reset Zustand store state
    useSidebarStore.setState({ isOpen: true })
  })

  describe('T051: Sidebar renders nav links and search', () => {
    it('should render all navigation links', () => {
      render(<Sidebar />)

      // Check for all expected navigation items
      expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /all tasks/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /focus mode/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /notes/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /achievements/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /settings/i })).toBeInTheDocument()
    })

    it('should render the Perpetua logo/brand', () => {
      render(<Sidebar />)

      expect(screen.getByText(/perpetua/i)).toBeInTheDocument()
    })

    it('should render a global search input', () => {
      render(<Sidebar />)

      // This will fail initially - search component not implemented yet
      expect(screen.getByRole('searchbox', { name: /global search/i })).toBeInTheDocument()
    })

    it('should render navigation items with icons', () => {
      render(<Sidebar />)

      // Verify icons are present by checking SVG elements
      const navLinks = screen.getAllByRole('link')
      navLinks.forEach((link) => {
        const svg = link.querySelector('svg')
        expect(svg).toBeInTheDocument()
      })
    })
  })

  describe('T052: Sidebar collapse persists in localStorage', () => {
    it('should toggle sidebar when collapse button is clicked', async () => {
      const user = userEvent.setup()
      render(<Sidebar />)

      // Find the close/collapse button
      const collapseButton = screen.getByRole('button', { name: /close sidebar/i })

      // Initial state should be open
      expect(useSidebarStore.getState().isOpen).toBe(true)

      // Click to collapse
      await user.click(collapseButton)

      // Sidebar should be closed
      expect(useSidebarStore.getState().isOpen).toBe(false)
    })

    it('should persist sidebar state to localStorage', async () => {
      const user = userEvent.setup()
      render(<Sidebar />)

      const collapseButton = screen.getByRole('button', { name: /close sidebar/i })

      // Collapse sidebar
      await user.click(collapseButton)

      // Check localStorage for persisted state
      const persistedState = localStorage.getItem('sidebar-storage')
      expect(persistedState).toBeTruthy()

      const parsedState = JSON.parse(persistedState!)
      expect(parsedState.state.isOpen).toBe(false)
    })

    it('should restore sidebar state from localStorage on mount', () => {
      // Set initial localStorage state to collapsed
      localStorage.setItem(
        'sidebar-storage',
        JSON.stringify({
          state: { isOpen: false },
          version: 0,
        })
      )

      render(<Sidebar />)

      // Sidebar should restore collapsed state
      expect(useSidebarStore.getState().isOpen).toBe(false)
    })

    it('should apply correct CSS classes when collapsed', async () => {
      const user = userEvent.setup()
      const { container } = render(<Sidebar />)

      const collapseButton = screen.getByRole('button', { name: /close sidebar/i })
      const sidebar = container.querySelector('aside')

      // Initially should not have -translate-x-full
      expect(sidebar).not.toHaveClass('-translate-x-full')
      expect(sidebar).toHaveClass('translate-x-0')

      // Collapse sidebar
      await user.click(collapseButton)

      // Should have -translate-x-full class
      expect(sidebar).toHaveClass('-translate-x-full')
    })
  })
})
