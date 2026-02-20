/**
 * T181 / T156 — RED test for ConflictResolutionModal
 *
 * This test MUST fail before T112 implementation begins (component file absent).
 * After T112 is complete, all tests here should pass.
 *
 * Acceptance criteria (T112 / FR-002):
 * - Shows side-by-side diff: "Your version" vs "Server version"
 * - "Keep mine" button calls onKeepMine handler
 * - "Take theirs" button calls onTakeTheirs handler
 * - "Cancel" dismisses (calls onCancel)
 */

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ConflictResolutionModal } from '@/components/tasks/ConflictResolutionModal'
import type { Task } from '@/lib/schemas/task.schema'

const baseTask: Task = {
  id: 'task-1',
  user_id: 'user-1',
  template_id: null,
  title: 'My local version',
  description: 'Local description',
  priority: 'medium',
  due_date: null,
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
  version: 2,
}

const serverTask: Task = {
  ...baseTask,
  title: 'Updated title from server',
  description: 'Server description',
  version: 3,
}

describe('ConflictResolutionModal', () => {
  const mockOnKeepMine = jest.fn()
  const mockOnTakeTheirs = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when open', () => {
    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('shows "Your version" panel with local task data', () => {
    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByText(/your version/i)).toBeInTheDocument()
    expect(screen.getByText('My local version')).toBeInTheDocument()
  })

  it('shows "Server version" panel with server task data', () => {
    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByText(/server version/i)).toBeInTheDocument()
    expect(screen.getByText('Updated title from server')).toBeInTheDocument()
  })

  it('calls onKeepMine when "Keep mine" button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    await user.click(screen.getByRole('button', { name: /keep mine/i }))
    expect(mockOnKeepMine).toHaveBeenCalledTimes(1)
  })

  it('calls onTakeTheirs when "Take theirs" button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    await user.click(screen.getByRole('button', { name: /take theirs/i }))
    expect(mockOnTakeTheirs).toHaveBeenCalledTimes(1)
  })

  it('calls onCancel when "Cancel" button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <ConflictResolutionModal
        isOpen={true}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    await user.click(screen.getByRole('button', { name: /cancel/i }))
    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('does not render dialog when isOpen is false', () => {
    render(
      <ConflictResolutionModal
        isOpen={false}
        localVersion={baseTask}
        serverVersion={serverTask}
        onKeepMine={mockOnKeepMine}
        onTakeTheirs={mockOnTakeTheirs}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})
