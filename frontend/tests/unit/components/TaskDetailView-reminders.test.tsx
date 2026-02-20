/**
 * T164 — RED test: TaskDetailView reminder wiring
 *
 * Tests:
 * 1. handleAddReminder calls useCreateReminder.mutateAsync with task payload
 * 2. Success toast appears only after promise resolves
 * 3. Error toast shown on rejection
 * 4. handleDeleteReminder calls useDeleteReminder.mutateAsync with reminderId
 *
 * Acceptance criteria: stub handlers fail these tests before T126; zero after.
 */

import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TaskDetailView } from '@/components/tasks/TaskDetailView'
import * as useRemindersModule from '@/lib/hooks/useReminders'
import * as useTasksModule from '@/lib/hooks/useTasks'
import * as useSubtasksModule from '@/lib/hooks/useSubtasks'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

// Mock next/link
jest.mock('next/link', () => {
  const LinkMock = ({ children, href }: { children: React.ReactNode; href: string }) =>
    React.createElement('a', { href }, children)
  LinkMock.displayName = 'Link'
  return LinkMock
})

// Mock useToast
const mockToast = jest.fn()
jest.mock('@/lib/hooks/useToast', () => ({
  useToast: () => ({ toast: mockToast }),
}))

// Mock stores
jest.mock('@/lib/stores/new-task-modal.store', () => ({
  useNewTaskModalStore: () => jest.fn(),
}))

jest.mock('@/lib/stores/useFocusStore', () => ({
  useFocusStore: () => ({ activate: jest.fn() }),
}))

// Mock useSubtasks
jest.mock('@/lib/hooks/useSubtasks', () => ({
  useSubtasks: () => ({ data: { data: [] }, isLoading: false }),
}))

// Mock ReminderSection so it exposes an "Add reminder" button we can click
jest.mock('@/components/reminders/ReminderSection', () => ({
  ReminderSection: ({
    onAddReminder,
    onDeleteReminder,
  }: {
    task: unknown
    reminders: unknown[]
    onAddReminder: (r: object) => void
    onDeleteReminder: (id: string) => void
  }) =>
    React.createElement(
      'div',
      { 'data-testid': 'reminder-section' },
      React.createElement(
        'button',
        {
          'data-testid': 'add-reminder-btn',
          onClick: () =>
            onAddReminder({
              type: 'before_due',
              offset_minutes: -15,
              scheduled_at: '2026-01-01T00:00:00Z',
            }),
        },
        'Add Reminder'
      ),
      React.createElement(
        'button',
        {
          'data-testid': 'delete-reminder-btn',
          onClick: () => onDeleteReminder('reminder-id-1'),
        },
        'Delete Reminder'
      )
    ),
}))

// Mock useTasks hooks
jest.mock('@/lib/hooks/useTasks', () => ({
  useUpdateTask: () => ({ mutateAsync: jest.fn(), isPending: false }),
  useDeleteTask: () => ({ mutateAsync: jest.fn(), isPending: false }),
}))

// Mock useReminders with controllable mutateAsync
const mockCreateMutateAsync = jest.fn()
const mockDeleteMutateAsync = jest.fn()

jest.mock('@/lib/hooks/useReminders', () => ({
  useCreateReminder: () => ({ mutateAsync: mockCreateMutateAsync }),
  useDeleteReminder: () => ({ mutateAsync: mockDeleteMutateAsync }),
  useReminders: () => ({ data: { data: [] } }),
}))

const mockTask = {
  id: 'task-1',
  user_id: 'user-1',
  template_id: null,
  title: 'Test Task',
  description: 'A task for testing',
  priority: 'medium' as const,
  due_date: '2026-12-31T00:00:00Z',
  estimated_duration: null,
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

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(
    React.createElement(QueryClientProvider, { client: queryClient }, ui)
  )
}

describe('T164 — TaskDetailView reminder wiring', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('handleAddReminder calls useCreateReminder.mutateAsync (not a stub)', async () => {
    const user = userEvent.setup()
    mockCreateMutateAsync.mockResolvedValue({
      data: {
        id: 'reminder-1',
        task_id: 'task-1',
        user_id: 'user-1',
        type: 'before_due',
        offset_minutes: -15,
        method: 'in_app',
        scheduled_at: '2026-01-01T00:00:00Z',
        fired: false,
        fired_at: null,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    })

    renderWithProviders(React.createElement(TaskDetailView, { task: mockTask as any }))

    await user.click(screen.getByTestId('add-reminder-btn'))

    await waitFor(() => {
      expect(mockCreateMutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'before_due',
          offset_minutes: -15,
        })
      )
    })
  })

  it('shows success toast only after mutateAsync resolves', async () => {
    const user = userEvent.setup()
    let resolveCreate!: (v: unknown) => void
    mockCreateMutateAsync.mockReturnValue(
      new Promise((resolve) => {
        resolveCreate = resolve
      })
    )

    renderWithProviders(React.createElement(TaskDetailView, { task: mockTask as any }))

    await user.click(screen.getByTestId('add-reminder-btn'))

    // Toast should NOT have been called yet (promise still pending)
    expect(mockToast).not.toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Reminder added' })
    )

    // Now resolve
    resolveCreate({
      data: {
        id: 'reminder-1',
        task_id: 'task-1',
        user_id: 'user-1',
        type: 'before_due',
        offset_minutes: -15,
        method: 'in_app',
        scheduled_at: '2026-01-01T00:00:00Z',
        fired: false,
        fired_at: null,
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    })

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Reminder added' })
      )
    })
  })

  it('shows error toast when mutateAsync rejects', async () => {
    const user = userEvent.setup()
    mockCreateMutateAsync.mockRejectedValue(new Error('Network error'))

    renderWithProviders(React.createElement(TaskDetailView, { task: mockTask as any }))

    await user.click(screen.getByTestId('add-reminder-btn'))

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          type: 'error',
        })
      )
    })
  })

  it('handleDeleteReminder calls useDeleteReminder.mutateAsync with reminderId', async () => {
    const user = userEvent.setup()
    mockDeleteMutateAsync.mockResolvedValue(undefined)

    renderWithProviders(React.createElement(TaskDetailView, { task: mockTask as any }))

    await user.click(screen.getByTestId('delete-reminder-btn'))

    await waitFor(() => {
      expect(mockDeleteMutateAsync).toHaveBeenCalledWith('reminder-id-1')
    })
  })
})
