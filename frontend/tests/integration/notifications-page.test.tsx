/**
 * T174 — RED test: notifications page route renders
 *
 * Tests:
 * 1. Component is not undefined/404
 * 2. useNotifications() hook is called
 * 3. Loading skeleton renders while fetching
 * 4. Empty state renders when data.length === 0
 *
 * Acceptance criteria: Test reports missing-component failures before T128; zero failures after.
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import NotificationsPage from '@/app/dashboard/notifications/page'
import * as useNotificationsModule from '@/lib/hooks/useNotifications'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
  usePathname: () => '/dashboard/notifications',
}))

// Mock next/link
jest.mock('next/link', () => {
  const LinkMock = ({ children, href }: { children: React.ReactNode; href: string }) =>
    React.createElement('a', { href }, children)
  LinkMock.displayName = 'Link'
  return LinkMock
})

jest.mock('@/lib/hooks/useNotifications')

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children)
}

describe('T174 — notifications page', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('component is not undefined — page module exists', () => {
    expect(NotificationsPage).toBeDefined()
    expect(typeof NotificationsPage).toBe('function')
  })

  it('calls useNotifications() hook', () => {
    const mockUseNotifications = jest.spyOn(useNotificationsModule, 'useNotifications')
    mockUseNotifications.mockReturnValue({
      data: { data: [], pagination: { offset: 0, limit: 25, total: 0, has_more: false } },
      isLoading: false,
      isError: false,
    } as any)

    const { container } = render(
      React.createElement(NotificationsPage),
      { wrapper: createWrapper() }
    )

    expect(mockUseNotifications).toHaveBeenCalled()
    expect(container).toBeTruthy()
  })

  it('renders loading skeleton while isLoading is true', () => {
    const mockUseNotifications = jest.spyOn(useNotificationsModule, 'useNotifications')
    mockUseNotifications.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as any)

    render(React.createElement(NotificationsPage), { wrapper: createWrapper() })

    // Loading state should show skeleton or loading indicator
    const loadingEl = screen.queryByTestId('notifications-loading') ??
      screen.queryByRole('status') ??
      document.querySelector('[aria-label="Loading notifications"]') ??
      document.querySelector('.animate-pulse')
    expect(loadingEl).toBeTruthy()
  })

  it('renders empty state when data.length === 0', () => {
    const mockUseNotifications = jest.spyOn(useNotificationsModule, 'useNotifications')
    mockUseNotifications.mockReturnValue({
      data: { data: [], pagination: { offset: 0, limit: 25, total: 0, has_more: false } },
      isLoading: false,
      isError: false,
    } as any)

    render(React.createElement(NotificationsPage), { wrapper: createWrapper() })

    // Empty state text
    expect(screen.getByText(/no notifications/i)).toBeTruthy()
  })
})
