/**
 * T053 [P] [US8] Test: Active route highlights in navigation
 * T054 [P] [US8] Test: Focus Mode hides sidebar (FR-039)
 */

import { render, screen } from '@testing-library/react'
import { Sidebar } from '@/components/layout/Sidebar'
import { useFocusStore } from '@/lib/stores/useFocusStore'

// Mock Next.js navigation
const mockPathname = jest.fn()
jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
}))

describe('Navigation Integration Tests - RED Tests', () => {
  beforeEach(() => {
    // Reset stores before each test
    localStorage.clear()
    mockPathname.mockReturnValue('/')
  })

  describe('T053: Active route highlights', () => {
    it('should highlight Dashboard nav item when on / route', () => {
      mockPathname.mockReturnValue('/')
      render(<Sidebar />)

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })

      // Active link should have specific styling classes
      expect(dashboardLink).toHaveClass('bg-blue-50')
      expect(dashboardLink).toHaveClass('text-blue-700')
    })

    it('should highlight All Tasks nav item when on /tasks route', () => {
      mockPathname.mockReturnValue('/tasks')
      render(<Sidebar />)

      const tasksLink = screen.getByRole('link', { name: /all tasks/i })

      // Active link should have highlight classes
      expect(tasksLink).toHaveClass('bg-blue-50')
      expect(tasksLink).toHaveClass('text-blue-700')
    })

    it('should highlight Focus Mode nav item when on /focus route', () => {
      mockPathname.mockReturnValue('/focus')
      render(<Sidebar />)

      const focusLink = screen.getByRole('link', { name: /focus mode/i })

      // Active link should have highlight classes
      expect(focusLink).toHaveClass('bg-blue-50')
      expect(focusLink).toHaveClass('text-blue-700')
    })

    it('should highlight Notes nav item when on /notes route', () => {
      mockPathname.mockReturnValue('/notes')
      render(<Sidebar />)

      const notesLink = screen.getByRole('link', { name: /notes/i })

      expect(notesLink).toHaveClass('bg-blue-50')
      expect(notesLink).toHaveClass('text-blue-700')
    })

    it('should highlight Achievements nav item when on /achievements route', () => {
      mockPathname.mockReturnValue('/achievements')
      render(<Sidebar />)

      const achievementsLink = screen.getByRole('link', { name: /achievements/i })

      expect(achievementsLink).toHaveClass('bg-blue-50')
      expect(achievementsLink).toHaveClass('text-blue-700')
    })

    it('should highlight Settings nav item when on /settings route', () => {
      mockPathname.mockReturnValue('/settings')
      render(<Sidebar />)

      const settingsLink = screen.getByRole('link', { name: /settings/i })

      expect(settingsLink).toHaveClass('bg-blue-50')
      expect(settingsLink).toHaveClass('text-blue-700')
    })

    it('should only highlight one nav item at a time', () => {
      mockPathname.mockReturnValue('/tasks')
      render(<Sidebar />)

      const allLinks = screen.getAllByRole('link')
      const activeLinks = allLinks.filter((link) =>
        link.className.includes('bg-blue-50')
      )

      // Only the Tasks link should be highlighted
      expect(activeLinks).toHaveLength(1)
      expect(activeLinks[0]).toHaveTextContent(/all tasks/i)
    })

    it('should not highlight any nav items on unknown routes', () => {
      mockPathname.mockReturnValue('/unknown-route')
      render(<Sidebar />)

      const allLinks = screen.getAllByRole('link')
      const activeLinks = allLinks.filter((link) =>
        link.className.includes('bg-blue-50')
      )

      // No links should be highlighted (except brand link which isn't in navItems)
      expect(activeLinks).toHaveLength(0)
    })
  })

  describe('T054: Focus Mode hides sidebar', () => {
    it('should hide sidebar when Focus Mode is active', () => {
      mockPathname.mockReturnValue('/')
      const { container } = render(<Sidebar />)

      // Activate Focus Mode
      useFocusStore.setState({ isActive: true, activeTaskId: 'task-123' })

      // Re-render to apply state change
      const { container: updatedContainer } = render(<Sidebar />)
      const sidebar = updatedContainer.querySelector('aside')

      // Sidebar should be hidden when Focus Mode is active
      // This will fail initially - Focus Mode integration not implemented yet
      expect(sidebar).toHaveClass('hidden')
    })

    it('should show sidebar when Focus Mode is inactive', () => {
      mockPathname.mockReturnValue('/')
      const { container } = render(<Sidebar />)

      // Ensure Focus Mode is inactive
      useFocusStore.setState({ isActive: false, activeTaskId: null })

      const sidebar = container.querySelector('aside')

      // Sidebar should be visible
      expect(sidebar).not.toHaveClass('hidden')
    })

    it('should completely remove sidebar from DOM during Focus Mode', () => {
      mockPathname.mockReturnValue('/')

      // Activate Focus Mode before render
      useFocusStore.setState({ isActive: true, activeTaskId: 'task-123' })

      const { container } = render(<Sidebar />)

      // Sidebar should not be in DOM at all during Focus Mode
      const sidebar = container.querySelector('aside')
      expect(sidebar).toBeNull()
    })

    it('should restore sidebar when exiting Focus Mode', () => {
      mockPathname.mockReturnValue('/')

      // Start with Focus Mode active
      useFocusStore.setState({ isActive: true, activeTaskId: 'task-123' })

      const { container, rerender } = render(<Sidebar />)

      // Sidebar should be hidden
      let sidebar = container.querySelector('aside')
      expect(sidebar).toBeNull()

      // Exit Focus Mode
      useFocusStore.setState({ isActive: false, activeTaskId: null })
      rerender(<Sidebar />)

      // Sidebar should be visible again
      sidebar = container.querySelector('aside')
      expect(sidebar).not.toBeNull()
      expect(sidebar).toBeInTheDocument()
    })
  })
})
