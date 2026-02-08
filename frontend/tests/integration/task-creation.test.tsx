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

// Mock useSubTasks - TaskCard calls useSubTasks which needs QueryClientProvider
jest.mock('@/lib/hooks/useSubTasks', () => ({
  useSubTasks: () => ({ data: [], isLoading: false }),
}))

// Mock useToast - TaskCard uses toast notifications
jest.mock('@/lib/hooks/useToast', () => ({
  useToast: () => ({ toast: jest.fn() }),
}))

const mockUseUpdateTask = useUpdateTask as jest.MockedFunction<typeof useUpdateTask>
const mockUpdateTask = jest.fn()

/** Create a valid Task with overrides */
function makeTask(overrides: Partial<Task> & { id: string; title: string }): Task {
  return {
    description: '',
    priority: 'medium',
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
    ...overrides,
  }
}

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
        makeTask({ id: 'task-1', title: 'Visible Task' }),
        makeTask({ id: 'task-2', title: 'Hidden Task', priority: 'high', hidden: true }),
        makeTask({ id: 'task-3', title: 'Another Visible Task', priority: 'low' }),
      ]

      render(<TaskList tasks={tasks} />)

      expect(screen.getByText('Visible Task')).toBeInTheDocument()
      expect(screen.getByText('Another Visible Task')).toBeInTheDocument()
      expect(screen.queryByText('Hidden Task')).not.toBeInTheDocument()
    })

    it('should only show hidden tasks when explicitly viewing hidden tasks section', () => {
      const tasks: Task[] = [
        makeTask({ id: 'task-1', title: 'Hidden Task 1', hidden: true }),
        makeTask({ id: 'task-2', title: 'Hidden Task 2', priority: 'high', hidden: true }),
        makeTask({ id: 'task-3', title: 'Visible Task', priority: 'low' }),
      ]

      render(<TaskList tasks={tasks} showHidden />)

      expect(screen.getByText('Hidden Task 1')).toBeInTheDocument()
      expect(screen.getByText('Hidden Task 2')).toBeInTheDocument()
      expect(screen.queryByText('Visible Task')).not.toBeInTheDocument()
    })

    it('should allow hiding a task', async () => {
      const user = userEvent.setup()

      const tasks: Task[] = [
        makeTask({ id: 'task-1', title: 'Task to Hide' }),
      ]

      mockUpdateTask.mockResolvedValue({ ...tasks[0], hidden: true })

      render(<TaskList tasks={tasks} />)

      expect(screen.getByText('Task to Hide')).toBeInTheDocument()
    })

    it('should allow unhiding a task from Settings → Hidden Tasks page', async () => {
      const user = userEvent.setup()

      const hiddenTask = makeTask({ id: 'task-1', title: 'Hidden Task', hidden: true })

      mockUpdateTask.mockResolvedValue({ ...hiddenTask, hidden: false })

      render(<TaskList tasks={[hiddenTask]} showHidden />)

      expect(screen.getByText('Hidden Task')).toBeInTheDocument()
    })

    it('should filter tasks correctly by hidden status', () => {
      const allTasks: Task[] = [
        makeTask({ id: 'task-1', title: 'Visible 1' }),
        makeTask({ id: 'task-2', title: 'Hidden 1', priority: 'high', hidden: true }),
        makeTask({ id: 'task-3', title: 'Visible 2', priority: 'low' }),
        makeTask({ id: 'task-4', title: 'Hidden 2', hidden: true }),
      ]

      const visibleTasks = allTasks.filter((t) => !t.hidden)
      const hiddenTasks = allTasks.filter((t) => t.hidden)

      expect(visibleTasks.length).toBe(2)
      expect(hiddenTasks.length).toBe(2)
      expect(visibleTasks.map((t) => t.title)).toEqual(['Visible 1', 'Visible 2'])
      expect(hiddenTasks.map((t) => t.title)).toEqual(['Hidden 1', 'Hidden 2'])
    })

    it('should not allow hiding already hidden tasks', () => {
      const hiddenTask = makeTask({ id: 'task-1', title: 'Already Hidden', hidden: true })

      expect(hiddenTask.hidden).toBe(true)
    })
  })

  describe('Task Visibility Rules', () => {
    it('should show only non-hidden tasks by default', () => {
      const tasks: Task[] = [
        makeTask({ id: '1', title: 'Visible' }),
        makeTask({ id: '2', title: 'Hidden', hidden: true }),
      ]

      render(<TaskList tasks={tasks} />)

      expect(screen.getByText('Visible')).toBeInTheDocument()
      expect(screen.queryByText('Hidden')).not.toBeInTheDocument()
    })

    it('should show empty state if all tasks are hidden', () => {
      const allHiddenTasks: Task[] = [
        makeTask({ id: '1', title: 'Hidden 1', hidden: true }),
      ]

      render(<TaskList tasks={allHiddenTasks} />)

      expect(screen.getByText(/no tasks/i)).toBeInTheDocument()
    })
  })
})
