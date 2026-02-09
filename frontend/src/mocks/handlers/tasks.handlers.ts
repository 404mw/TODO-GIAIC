import { http, HttpResponse, delay } from 'msw'
import type { Task } from '@/lib/schemas/task.schema'
import type { SubTask } from '@/lib/schemas/subtask.schema'
import { TaskSchema, TaskUpdateSchema } from '@/lib/schemas/task.schema'
import { SubTaskSchema, SubTaskUpdateSchema } from '@/lib/schemas/subtask.schema'
import { tasksFixture } from '../data/tasks.fixture'
import { subtasksFixture } from '../data/subtasks.fixture'
import { onTaskComplete } from '@/lib/utils/recurrence'

// In-memory storage (will be replaced with MSW database pattern)
let tasks: Task[] = [...tasksFixture]
let subtasks: SubTask[] = [...subtasksFixture]

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Helper: Generate UUID
const generateUUID = () => crypto.randomUUID()

// Helper: Calculate task progress
const calculateTaskProgress = (taskId: string): number => {
  const taskSubtasks = subtasks.filter(st => st.parentTaskId === taskId)
  if (taskSubtasks.length === 0) return 0
  const completed = taskSubtasks.filter(st => st.completed).length
  return Math.round((completed / taskSubtasks.length) * 100)
}

// Helper: Generate next recurring instance
// T107: Use centralized recurrence utility (FR-070)
// Replaced with onTaskComplete from @/lib/utils/recurrence
const generateNextRecurringInstance = onTaskComplete

// GET /api/tasks - List all tasks with filters
export const getTasksHandler = http.get('/api/tasks', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const hidden = url.searchParams.get('hidden')
  const archived = url.searchParams.get('archived')
  const priority = url.searchParams.get('priority')

  let filtered = tasks

  if (hidden === 'true') {
    filtered = filtered.filter(t => t.hidden)
  } else if (hidden === 'false') {
    filtered = filtered.filter(t => !t.hidden)
  }

  if (archived === 'true') {
    filtered = filtered.filter(t => t.completed)
  } else if (archived === 'false') {
    filtered = filtered.filter(t => !t.completed)
  }

  if (priority) {
    filtered = filtered.filter(t => t.priority === priority)
  }

  return HttpResponse.json(filtered, { status: 200 })
})

// GET /api/tasks/:id - Get single task
export const getTaskHandler = http.get('/api/tasks/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const task = tasks.find(t => t.id === id)

  if (!task) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
      { status: 404 }
    )
  }

  return HttpResponse.json(task, { status: 200 })
})

// POST /api/tasks - Create new task
export const createTaskHandler = http.post('/api/tasks', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    const now = new Date().toISOString()
    const newTask: Task = {
      id: generateUUID(),
      ...(body as any),
      createdAt: now,
      updatedAt: now,
      completedAt: null,
      hidden: false,
      completed: false,
      parentTaskId: null,
      isRecurringInstance: false,
    }

    TaskSchema.parse(newTask)
    tasks.push(newTask)

    return HttpResponse.json(newTask, { status: 201 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid task data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// PATCH /api/tasks/:id - Update task
export const updateTaskHandler = http.patch('/api/tasks/:id', async ({ params, request }) => {
  await simulateLatency()

  const { id } = params
  const body = await request.json()
  const taskIndex = tasks.findIndex(t => t.id === id)

  if (taskIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
      { status: 404 }
    )
  }

  try {
    TaskUpdateSchema.parse(body)

    const task = tasks[taskIndex]
    const updatedTask: Task = {
      ...task,
      ...(body as any),
      updatedAt: new Date().toISOString(),
    }

    // Set completedAt when marking as complete
    if ((body as any)?.completed === true && !task.completed) {
      updatedTask.completed_at = new Date().toISOString()
    }

    tasks[taskIndex] = updatedTask

    // Generate next recurring instance if task is recurring and completed
    let nextInstance: Task | null = null
    if ((body as any)?.completed === true && updatedTask.recurrence?.enabled) {
      nextInstance = generateNextRecurringInstance(updatedTask)
      if (nextInstance) {
        tasks.push(nextInstance)
      }
    }

    return HttpResponse.json(
      nextInstance ? { task: updatedTask, nextInstance } : { task: updatedTask },
      { status: 200 }
    )
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid update data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// DELETE /api/tasks/:id - Soft delete task (set hidden=true)
export const deleteTaskHandler = http.delete('/api/tasks/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const taskIndex = tasks.findIndex(t => t.id === id)

  if (taskIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
      { status: 404 }
    )
  }

  tasks[taskIndex].hidden = true
  tasks[taskIndex].updated_at = new Date().toISOString()

  return HttpResponse.json(null, { status: 204 })
})

// GET /api/tasks/:id/sub-tasks - Get subtasks for a task
export const getSubTasksHandler = http.get('/api/tasks/:id/sub-tasks', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const task = tasks.find(t => t.id === id)

  if (!task) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
      { status: 404 }
    )
  }

  const taskSubtasks = subtasks.filter(st => st.parentTaskId === id)
  return HttpResponse.json(taskSubtasks, { status: 200 })
})

// POST /api/tasks/:id/sub-tasks - Create subtask
export const createSubTaskHandler = http.post('/api/tasks/:id/sub-tasks', async ({ params, request }) => {
  await simulateLatency()

  const { id } = params
  const body = await request.json()
  const task = tasks.find(t => t.id === id)

  if (!task) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Task not found' } },
      { status: 404 }
    )
  }

  // Check max subtasks limit
  const existingSubtasks = subtasks.filter(st => st.parentTaskId === id)
  if (existingSubtasks.length >= 10) {
    return HttpResponse.json(
      {
        error: {
          code: 'NESTING_LIMIT_EXCEEDED',
          message: 'Maximum 10 subtasks per task',
        },
      },
      { status: 400 }
    )
  }

  try {
    const now = new Date().toISOString()
    const newSubtask: SubTask = {
      id: generateUUID(),
      ...(body as any),
      parentTaskId: id as string,
      createdAt: now,
      updatedAt: now,
      completedAt: null,
      completed: false,
    }

    SubTaskSchema.parse(newSubtask)
    subtasks.push(newSubtask)

    return HttpResponse.json(newSubtask, { status: 201 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid subtask data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// PATCH /api/tasks/:id/sub-tasks/:subTaskId - Update subtask
export const updateSubTaskHandler = http.patch(
  '/api/tasks/:id/sub-tasks/:subTaskId',
  async ({ params, request }) => {
    await simulateLatency()

    const { id, subTaskId } = params
    const body = await request.json()
    const subtaskIndex = subtasks.findIndex(st => st.id === subTaskId && st.parentTaskId === id)

    if (subtaskIndex === -1) {
      return HttpResponse.json(
        { error: { code: 'RESOURCE_NOT_FOUND', message: 'Subtask not found' } },
        { status: 404 }
      )
    }

    try {
      SubTaskUpdateSchema.parse(body)

      const subtask = subtasks[subtaskIndex]
      const updatedSubtask: SubTask = {
        ...subtask,
        ...(body as any),
        updatedAt: new Date().toISOString(),
      }

      // Set completedAt when marking as complete
      if ((body as any)?.completed === true && !subtask.completed) {
        updatedSubtask.completed_at = new Date().toISOString()
      } else if ((body as any)?.completed === false) {
        updatedSubtask.completed_at = null
      }

      subtasks[subtaskIndex] = updatedSubtask

      return HttpResponse.json(updatedSubtask, { status: 200 })
    } catch (error) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid subtask update data',
            details: error,
          },
        },
        { status: 400 }
      )
    }
  }
)

// DELETE /api/tasks/:id/sub-tasks/:subTaskId - Delete subtask
export const deleteSubTaskHandler = http.delete(
  '/api/tasks/:id/sub-tasks/:subTaskId',
  async ({ params }) => {
    await simulateLatency()

    const { id, subTaskId } = params
    const subtaskIndex = subtasks.findIndex(st => st.id === subTaskId && st.parentTaskId === id)

    if (subtaskIndex === -1) {
      return HttpResponse.json(
        { error: { code: 'RESOURCE_NOT_FOUND', message: 'Subtask not found' } },
        { status: 404 }
      )
    }

    subtasks.splice(subtaskIndex, 1)
    return HttpResponse.json(null, { status: 204 })
  }
)

// Export all task handlers
export const tasksHandlers = [
  getTasksHandler,
  getTaskHandler,
  createTaskHandler,
  updateTaskHandler,
  deleteTaskHandler,
  getSubTasksHandler,
  createSubTaskHandler,
  updateSubTaskHandler,
  deleteSubTaskHandler,
]
