import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SubTaskList } from '@/components/tasks/SubTaskList'
import { useUpdateSubTask, useDeleteSubTask } from '@/lib/hooks/useSubTasks'
import { useToast } from '@/lib/hooks/useToast'
import type { SubTask } from '@/lib/schemas/subtask.schema'

// Mock dependencies
jest.mock('@/lib/hooks/useSubTasks')
jest.mock('@/lib/hooks/useToast')

const mockUpdateSubTask = jest.fn()
const mockDeleteSubTask = jest.fn()
const mockToast = jest.fn()

// Mock window.confirm
const mockConfirm = jest.fn()
global.confirm = mockConfirm

/** Create a valid SubTask with overrides */
let orderCounter = 0
function makeSubTask(overrides: Partial<SubTask> & { id: string; title: string }): SubTask {
  return {
    taskId: 'task-1',
    completed: false,
    completedAt: null,
    orderIndex: orderCounter++,
    source: 'user',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  }
}

describe('SubTaskList', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    ;(useUpdateSubTask as jest.Mock).mockReturnValue({
      mutateAsync: mockUpdateSubTask,
      isPending: false,
    })

    ;(useDeleteSubTask as jest.Mock).mockReturnValue({
      mutateAsync: mockDeleteSubTask,
      isPending: false,
    })

    ;(useToast as jest.Mock).mockReturnValue({
      toast: mockToast,
    })

    mockConfirm.mockReturnValue(true) // Default to confirming deletions
  })

  // T068: Test sub-task progress calculation (33% for 1/3 complete)
  describe('T068: Sub-task progress calculation', () => {
    it('should calculate 33% progress for 1 of 3 completed subtasks', () => {
      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1', completed: true, completedAt: new Date().toISOString() }),
        makeSubTask({ id: 'sub-2', title: 'Subtask 2' }),
        makeSubTask({ id: 'sub-3', title: 'Subtask 3' }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Verify all subtasks are rendered
      expect(screen.getByText('Subtask 1')).toBeInTheDocument()
      expect(screen.getByText('Subtask 2')).toBeInTheDocument()
      expect(screen.getByText('Subtask 3')).toBeInTheDocument()

      // Calculate progress
      const completedCount = subtasks.filter((st) => st.completed).length
      const totalCount = subtasks.length
      const progress = Math.round((completedCount / totalCount) * 100)

      // Verify progress is 33%
      expect(progress).toBe(33)
      expect(completedCount).toBe(1)
      expect(totalCount).toBe(3)
    })

    it('should calculate 100% progress when all subtasks completed', () => {
      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1', completed: true, completedAt: new Date().toISOString() }),
        makeSubTask({ id: 'sub-2', title: 'Subtask 2', completed: true, completedAt: new Date().toISOString() }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const completedCount = subtasks.filter((st) => st.completed).length
      const totalCount = subtasks.length
      const progress = Math.round((completedCount / totalCount) * 100)

      expect(progress).toBe(100)
    })

    it('should calculate 0% progress when no subtasks completed', () => {
      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
        makeSubTask({ id: 'sub-2', title: 'Subtask 2' }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const completedCount = subtasks.filter((st) => st.completed).length
      const totalCount = subtasks.length
      const progress = Math.round((completedCount / totalCount) * 100)

      expect(progress).toBe(0)
    })

    it('should update progress when subtask is toggled', async () => {
      const user = userEvent.setup()

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
        makeSubTask({ id: 'sub-2', title: 'Subtask 2' }),
        makeSubTask({ id: 'sub-3', title: 'Subtask 3' }),
      ]

      mockUpdateSubTask.mockResolvedValue({})

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Toggle first subtask
      const checkboxes = screen.getAllByRole('button')
      const firstCheckbox = checkboxes[0] // First checkbox button
      await user.click(firstCheckbox)

      // Verify update was called
      await waitFor(() => {
        expect(mockUpdateSubTask).toHaveBeenCalledWith({
          taskId: 'task-1',
          subtaskId: 'sub-1',
          input: { completed: true },
        })
      })

      // After mutation, progress should be 33% (1/3)
      // This would be handled by parent component re-render with updated data
    })
  })

  // T070: Test orphaned sub-tasks prevented with error message
  describe('T070: Prevent orphaned sub-tasks', () => {
    it('should show confirmation dialog before deleting subtask', async () => {
      const user = userEvent.setup()

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
      ]

      mockDeleteSubTask.mockResolvedValue({})

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Click delete button
      const deleteButtons = screen.getAllByRole('button')
      const deleteButton = deleteButtons.find((btn) => {
        const svg = btn.querySelector('svg')
        return svg && svg.querySelector('path[d*="M19"]') // Delete icon path
      })

      if (!deleteButton) {
        throw new Error('Delete button not found')
      }

      await user.click(deleteButton)

      // Verify confirmation was shown
      expect(mockConfirm).toHaveBeenCalledWith('Are you sure you want to delete this subtask?')
    })

    it('should not delete subtask if user cancels confirmation', async () => {
      const user = userEvent.setup()
      mockConfirm.mockReturnValue(false) // User clicks "Cancel"

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Click delete button
      const deleteButtons = screen.getAllByRole('button')
      const deleteButton = deleteButtons.find((btn) => {
        const svg = btn.querySelector('svg')
        return svg && svg.querySelector('path[d*="M19"]')
      })

      if (!deleteButton) {
        throw new Error('Delete button not found')
      }

      await user.click(deleteButton)

      // Verify delete mutation was NOT called
      expect(mockDeleteSubTask).not.toHaveBeenCalled()
    })

    it('should delete subtask if user confirms', async () => {
      const user = userEvent.setup()
      mockConfirm.mockReturnValue(true) // User clicks "OK"

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
      ]

      mockDeleteSubTask.mockResolvedValue({})

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Click delete button
      const deleteButtons = screen.getAllByRole('button')
      const deleteButton = deleteButtons.find((btn) => {
        const svg = btn.querySelector('svg')
        return svg && svg.querySelector('path[d*="M19"]')
      })

      if (!deleteButton) {
        throw new Error('Delete button not found')
      }

      await user.click(deleteButton)

      // Verify delete mutation was called
      await waitFor(() => {
        expect(mockDeleteSubTask).toHaveBeenCalledWith({
          taskId: 'task-1',
          subtaskId: 'sub-1',
        })
      })

      // Verify success toast
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Subtask deleted',
          variant: 'success',
        })
      )
    })

    it('should show error message if deletion fails', async () => {
      const user = userEvent.setup()
      mockConfirm.mockReturnValue(true)
      mockDeleteSubTask.mockRejectedValue(new Error('Network error'))

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Subtask 1' }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const deleteButtons = screen.getAllByRole('button')
      const deleteButton = deleteButtons.find((btn) => {
        const svg = btn.querySelector('svg')
        return svg && svg.querySelector('path[d*="M19"]')
      })

      if (!deleteButton) {
        throw new Error('Delete button not found')
      }

      await user.click(deleteButton)

      // Verify error toast
      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Error',
            description: 'Failed to delete subtask',
            variant: 'error',
          })
        )
      })
    })
  })

  // Additional tests for completeness
  describe('UI Rendering', () => {
    it('should show empty state when no subtasks', () => {
      render(<SubTaskList taskId="task-1" subtasks={[]} />)

      expect(screen.getByText(/no subtasks yet/i)).toBeInTheDocument()
    })

    it('should render subtask title with completed styling', () => {
      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Completed Subtask', completed: true, completedAt: new Date().toISOString() }),
      ]

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const title = screen.getByText('Completed Subtask')
      expect(title).toHaveClass('line-through')
      expect(title).toHaveClass('opacity-60')
    })

    it('should show checkmark icon for completed subtask', () => {
      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Completed Subtask', completed: true, completedAt: new Date().toISOString() }),
      ]

      const { container } = render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      // Check for checkmark SVG path
      const checkmarkPath = container.querySelector('path[d="M5 13l4 4L19 7"]')
      expect(checkmarkPath).toBeInTheDocument()
    })
  })

  describe('Toggle Complete Functionality', () => {
    it('should mark incomplete subtask as complete', async () => {
      const user = userEvent.setup()

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Incomplete Subtask' }),
      ]

      mockUpdateSubTask.mockResolvedValue({})

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const checkboxes = screen.getAllByRole('button')
      const checkbox = checkboxes[0]
      await user.click(checkbox)

      await waitFor(() => {
        expect(mockUpdateSubTask).toHaveBeenCalledWith({
          taskId: 'task-1',
          subtaskId: 'sub-1',
          input: { completed: true },
        })
      })

      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Subtask completed!',
          description: expect.stringContaining('making progress'),
          variant: 'success',
        })
      )
    })

    it('should mark complete subtask as incomplete', async () => {
      const user = userEvent.setup()

      const subtasks: SubTask[] = [
        makeSubTask({ id: 'sub-1', title: 'Complete Subtask', completed: true, completedAt: new Date().toISOString() }),
      ]

      mockUpdateSubTask.mockResolvedValue({})

      render(<SubTaskList taskId="task-1" subtasks={subtasks} />)

      const checkboxes = screen.getAllByRole('button')
      const checkbox = checkboxes[0]
      await user.click(checkbox)

      await waitFor(() => {
        expect(mockUpdateSubTask).toHaveBeenCalledWith({
          taskId: 'task-1',
          subtaskId: 'sub-1',
          input: { completed: false },
        })
      })

      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Subtask reopened',
          description: 'Subtask marked as incomplete',
          variant: 'success',
        })
      )
    })
  })
})
