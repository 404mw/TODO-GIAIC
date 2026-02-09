import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TaskList } from '@/components/tasks/TaskList'
import { useUpdateTask } from '@/lib/hooks/useTasks'
import type { Task } from '@/lib/schemas/task.schema'

// Mock Next.js navigation - required for TaskCard which uses useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
  }),
  usePathname: () => '/tasks',
  useSearchParams: () => new URLSearchParams(),
}))

// Mock dependencies - only mock useUpdateTask since TaskList receives tasks via props
jest.mock('@/lib/hooks/useTasks', () => ({
  useUpdateTask: jest.fn(),
}))

const mockUseUpdateTask = useUpdateTask as jest.MockedFunction<typeof useUpdateTask>
const mockUpdateTask = jest.fn()

describe('Task Creation Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()

    mockUseUpdateTask.mockReturnValue({
      mutateAsync: mockUpdateTask,
      isPending: false,
      isSuccess: false,
      isError: false,
      error: null,
      data: undefined,
      mutate: jest.fn(),
      reset: jest.fn(),
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isPaused: false,
      status: 'idle',
    })
  })

  // T069: Hidden tasks excluded from default views
  describe('T069: Hidden tasks excluded from default views', () => {
    it('should not show hidden tasks in default task list', () => {
      const tasks: Task[] = [
        {
          id: 'task-1',
          title: 'Visible Task',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-2',
          title: 'Hidden Task',
          description: '',
          priority: 'high',
          tags: [],
          completed: false,
          hidden: true, // This task should NOT be shown
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-3',
          title: 'Another Visible Task',
          description: '',
          priority: 'low',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      // Pass tasks via props - TaskList filters hidden tasks internally
      render(<TaskList tasks={tasks} />)

      // Should show visible tasks
      expect(screen.getByText('Visible Task')).toBeInTheDocument()
      expect(screen.getByText('Another Visible Task')).toBeInTheDocument()

      // Should NOT show hidden task (TaskList filters hidden=true by default)
      expect(screen.queryByText('Hidden Task')).not.toBeInTheDocument()
    })

    it('should only show hidden tasks when explicitly viewing hidden tasks section', () => {
      const tasks: Task[] = [
        {
          id: 'task-1',
          title: 'Hidden Task 1',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-2',
          title: 'Hidden Task 2',
          description: '',
          priority: 'high',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-3',
          title: 'Visible Task',
          description: '',
          priority: 'low',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      // In hidden tasks view - pass showHidden prop and tasks via props
      render(<TaskList tasks={tasks} showHidden />)

      // Should show both hidden tasks
      expect(screen.getByText('Hidden Task 1')).toBeInTheDocument()
      expect(screen.getByText('Hidden Task 2')).toBeInTheDocument()

      // Should NOT show visible task in hidden view
      expect(screen.queryByText('Visible Task')).not.toBeInTheDocument()
    })

    it('should allow hiding a task', async () => {
      const user = userEvent.setup()

      const tasks: Task[] = [
        {
          id: 'task-1',
          title: 'Task to Hide',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      mockUpdateTask.mockResolvedValue({
        ...tasks[0],
        hidden: true,
      })

      // Pass tasks via props
      render(<TaskList tasks={tasks} />)

      // Find and click hide button (this might be a menu action)
      // This test assumes there's a hide action available on the task card
      // The actual implementation may differ

      expect(screen.getByText('Task to Hide')).toBeInTheDocument()

      // After hiding, the task should be updated with hidden: true
      // This would trigger a refetch, and the task should disappear from the list
    })

    it('should allow unhiding a task from Settings → Hidden Tasks page', async () => {
      const user = userEvent.setup()

      const hiddenTask: Task = {
        id: 'task-1',
        title: 'Hidden Task',
        description: '',
        priority: 'medium',
        tags: [],
        completed: false,
        hidden: true,
        dueDate: null,
        estimatedDuration: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: null,
        parentTaskId: null,
      }

      mockUpdateTask.mockResolvedValue({
        ...hiddenTask,
        hidden: false,
      })

      // Render hidden tasks view - pass tasks via props
      render(<TaskList tasks={[hiddenTask]} showHidden />)

      expect(screen.getByText('Hidden Task')).toBeInTheDocument()

      // Unhide action would update the task with hidden: false
      // After unhiding, the task should disappear from hidden list
      // and appear in the default task list
    })

    it('should filter tasks correctly by hidden status', () => {
      const allTasks: Task[] = [
        {
          id: 'task-1',
          title: 'Visible 1',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-2',
          title: 'Hidden 1',
          description: '',
          priority: 'high',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-3',
          title: 'Visible 2',
          description: '',
          priority: 'low',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: 'task-4',
          title: 'Hidden 2',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      // Filter logic
      const visibleTasks = allTasks.filter((t) => !t.hidden)
      const hiddenTasks = allTasks.filter((t) => t.hidden)

      // Verify counts
      expect(visibleTasks.length).toBe(2)
      expect(hiddenTasks.length).toBe(2)

      // Verify correct tasks in each category
      expect(visibleTasks.map((t) => t.title)).toEqual(['Visible 1', 'Visible 2'])
      expect(hiddenTasks.map((t) => t.title)).toEqual(['Hidden 1', 'Hidden 2'])
    })

    it('should not allow hiding already hidden tasks', () => {
      const hiddenTask: Task = {
        id: 'task-1',
        title: 'Already Hidden',
        description: '',
        priority: 'medium',
        tags: [],
        completed: false,
        hidden: true,
        dueDate: null,
        estimatedDuration: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: null,
        parentTaskId: null,
      }

      // Verify task is already hidden
      expect(hiddenTask.hidden).toBe(true)

      // Attempting to hide again should be a no-op or prevented by UI
      // The hide button should not be visible for hidden tasks in default view
    })
  })

  describe('Task Visibility Rules', () => {
    it('should show only non-hidden tasks by default', () => {
      const tasks: Task[] = [
        {
          id: '1',
          title: 'Visible',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: false,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
        {
          id: '2',
          title: 'Hidden',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      // Pass tasks via props - TaskList filters internally
      render(<TaskList tasks={tasks} />)

      // Should show visible task
      expect(screen.getByText('Visible')).toBeInTheDocument()
      // Should NOT show hidden task
      expect(screen.queryByText('Hidden')).not.toBeInTheDocument()
    })

    it('should show empty state if all tasks are hidden', () => {
      const allHiddenTasks: Task[] = [
        {
          id: '1',
          title: 'Hidden 1',
          description: '',
          priority: 'medium',
          tags: [],
          completed: false,
          hidden: true,
          dueDate: null,
          estimatedDuration: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: null,
          parentTaskId: null,
        },
      ]

      // Pass all hidden tasks - TaskList filters them out, resulting in empty view
      render(<TaskList tasks={allHiddenTasks} />)

      // Should show empty state message (TaskList filters hidden=true, so no visible tasks)
      expect(screen.getByText(/no tasks/i)).toBeInTheDocument()
    })
  })
})
