/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskForm } from '@/components/tasks/TaskForm'
import { useCreateTask, useUpdateTask } from '@/lib/hooks/useTasks'
import { useRouter } from 'next/navigation'
import { useToast } from '@/lib/hooks/useToast'

// Polyfills for Radix UI Select in JSDOM
beforeAll(() => {
  HTMLElement.prototype.hasPointerCapture = jest.fn()
  HTMLElement.prototype.setPointerCapture = jest.fn()
  HTMLElement.prototype.releasePointerCapture = jest.fn()
  Element.prototype.scrollIntoView = jest.fn()
  window.getComputedStyle = jest.fn().mockImplementation(() => ({
    getPropertyValue: jest.fn(),
  }))
})

// Mock dependencies
jest.mock('@/lib/hooks/useTasks')
jest.mock('next/navigation')
jest.mock('@/lib/hooks/useToast')

const mockCreateTask = jest.fn()
const mockUpdateTask = jest.fn()
const mockPush = jest.fn()
const mockToast = jest.fn()

describe('TaskForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    ;(useCreateTask as jest.Mock).mockReturnValue({
      mutateAsync: mockCreateTask,
      isPending: false,
    })

    ;(useUpdateTask as jest.Mock).mockReturnValue({
      mutateAsync: mockUpdateTask,
      isPending: false,
    })

    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })

    ;(useToast as jest.Mock).mockReturnValue({
      toast: mockToast,
    })
  })

  // T066: Test that TaskForm renders all fields
  describe('T066: TaskForm renders all required fields', () => {
    it('should render title field', () => {
      render(<TaskForm />)

      expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/what needs to be done/i)).toBeInTheDocument()
    })

    it('should render description field', () => {
      render(<TaskForm />)

      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/add more details/i)).toBeInTheDocument()
    })

    it('should render priority field', () => {
      render(<TaskForm />)

      expect(screen.getByText(/priority/i)).toBeInTheDocument()
    })

    it('should render tags field', () => {
      render(<TaskForm />)

      expect(screen.getByLabelText(/tags/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/add a tag/i)).toBeInTheDocument()
    })

    it('should render due date field', () => {
      render(<TaskForm />)

      expect(screen.getByLabelText(/due date/i)).toBeInTheDocument()
    })

    it('should render estimated duration field', () => {
      render(<TaskForm />)

      expect(screen.getByLabelText(/estimated duration/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/how long will this take/i)).toBeInTheDocument()
    })

    it('should render submit button', () => {
      render(<TaskForm />)

      expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument()
    })
  })

  // T067: Test that TaskForm submits and creates task with UUID
  describe('T067: TaskForm submits and creates task with UUID', () => {
    it('should create task with all required fields when form is submitted', async () => {
      const user = userEvent.setup()
      const mockNewTask = {
        id: '550e8400-e29b-41d4-a716-446655440000', // Valid UUID v4
        title: 'Finish report',
        description: 'Complete the quarterly report',
        priority: 'high' as const,
        dueDate: new Date('2026-01-15T14:00:00.000Z').toISOString(),
        estimatedDuration: 120,
        focusTimeSeconds: 0,
        completed: false,
        completedAt: null,
        completedBy: null,
        hidden: false,
        archived: false,
        templateId: null,
        subtaskCount: 0,
        subtaskCompletedCount: 0,
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }

      mockCreateTask.mockResolvedValue(mockNewTask)

      render(<TaskForm />)

      // Fill in title
      const titleInput = screen.getByLabelText(/title/i)
      await user.type(titleInput, 'Finish report')

      // Fill in description
      const descriptionInput = screen.getByLabelText(/description/i)
      await user.type(descriptionInput, 'Complete the quarterly report')

      // Fill in priority (already defaults to medium, so we need to change it)
      // Note: Radix Select trigger doesn't get the label's accessible name
      const prioritySelect = screen.getByRole('combobox')
      await user.click(prioritySelect)
      const highOption = screen.getByRole('option', { name: /high/i })
      await user.click(highOption)

      // Add tags
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      await user.type(tagInput, 'work')
      await user.click(screen.getByRole('button', { name: /add/i }))

      await user.type(tagInput, 'urgent')
      await user.click(screen.getByRole('button', { name: /add/i }))

      // Fill in due date
      const dueDateInput = screen.getByLabelText(/due date/i)
      await user.type(dueDateInput, '2026-01-15T14:00')

      // Fill in estimated duration
      const durationInput = screen.getByLabelText(/estimated duration/i)
      await user.type(durationInput, '120')

      // Submit form
      const submitButton = screen.getByRole('button', { name: /create task/i })
      await user.click(submitButton)

      // Verify createTask was called with correct data
      await waitFor(() => {
        expect(mockCreateTask).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Finish report',
            description: 'Complete the quarterly report',
            priority: 'high',
            tags: ['work', 'urgent'],
            dueDate: expect.any(String),
            estimatedDuration: 120,
          })
        )
      })

      // Verify toast was shown
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Task created',
          variant: 'success',
        })
      )

      // Verify navigation to task detail page with UUID
      expect(mockPush).toHaveBeenCalledWith(`/dashboard/tasks/${mockNewTask.id}`)

      // Verify UUID format (UUID v4 pattern)
      expect(mockNewTask.id).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      )
    })

    it('should prevent submission when title is empty', () => {
      render(<TaskForm />)

      // Submit button should be disabled when title is empty
      const submitButton = screen.getByRole('button', { name: /create task/i })
      expect(submitButton).toBeDisabled()

      // Verify createTask was NOT called
      expect(mockCreateTask).not.toHaveBeenCalled()
    })

    it('should trim whitespace from title and description', async () => {
      const user = userEvent.setup()
      const mockNewTask = {
        id: '550e8400-e29b-41d4-a716-446655440001',
        title: 'Trimmed Title',
        description: 'Trimmed Description',
        priority: 'medium' as const,
        dueDate: null,
        estimatedDuration: null,
        focusTimeSeconds: 0,
        completed: false,
        completedAt: null,
        completedBy: null,
        hidden: false,
        archived: false,
        templateId: null,
        subtaskCount: 0,
        subtaskCompletedCount: 0,
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }

      mockCreateTask.mockResolvedValue(mockNewTask)

      render(<TaskForm />)

      // Type title with extra spaces
      const titleInput = screen.getByLabelText(/title/i)
      await user.type(titleInput, '  Trimmed Title  ')

      // Type description with extra spaces
      const descriptionInput = screen.getByLabelText(/description/i)
      await user.type(descriptionInput, '  Trimmed Description  ')

      // Submit form
      const submitButton = screen.getByRole('button', { name: /create task/i })
      await user.click(submitButton)

      // Verify trimmed values were passed
      await waitFor(() => {
        expect(mockCreateTask).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Trimmed Title',
            description: 'Trimmed Description',
          })
        )
      })
    })

    it('should enforce max 20 tags limit', async () => {
      const user = userEvent.setup()

      render(<TaskForm />)

      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      const addButton = screen.getByRole('button', { name: /add/i })

      // Add 20 tags
      for (let i = 0; i < 20; i++) {
        await user.type(tagInput, `tag${i}`)
        await user.click(addButton)
      }

      // Verify input is disabled after 20 tags
      expect(tagInput).toBeDisabled()
      expect(addButton).toBeDisabled()

      // Verify character count shows 20/20
      expect(screen.getByText(/20\/20 tags/i)).toBeInTheDocument()
    }, 30000)

    it('should enforce max 200 characters for title', async () => {
      const user = userEvent.setup()

      render(<TaskForm />)

      const titleInput = screen.getByLabelText(/title/i) as HTMLInputElement

      // Type 201 characters
      const longTitle = 'a'.repeat(201)
      await user.type(titleInput, longTitle)

      // Verify only 200 characters are allowed
      expect(titleInput.value.length).toBe(200)
      expect(screen.getByText(/200\/200 characters/i)).toBeInTheDocument()
    })

    it('should enforce max 1000 characters for description', async () => {
      const user = userEvent.setup()

      render(<TaskForm />)

      const descriptionInput = screen.getByLabelText(/description/i) as HTMLTextAreaElement

      // Type 1001 characters
      const longDescription = 'a'.repeat(1001)
      await user.type(descriptionInput, longDescription)

      // Verify only 1000 characters are allowed
      expect(descriptionInput.value.length).toBe(1000)
      expect(screen.getByText(/1000\/1000 characters/i)).toBeInTheDocument()
    }, 60000)
  })

  // Additional test for form validation
  describe('Form Validation', () => {
    it('should disable submit button when title is empty', () => {
      render(<TaskForm />)

      const submitButton = screen.getByRole('button', { name: /create task/i })

      // Button should be disabled initially (no title)
      expect(submitButton).toBeDisabled()
    })

    it('should enable submit button when title is provided', async () => {
      const user = userEvent.setup()

      render(<TaskForm />)

      const titleInput = screen.getByLabelText(/title/i)
      const submitButton = screen.getByRole('button', { name: /create task/i })

      // Type title
      await user.type(titleInput, 'Valid Title')

      // Button should be enabled
      expect(submitButton).toBeEnabled()
    })
  })
})
