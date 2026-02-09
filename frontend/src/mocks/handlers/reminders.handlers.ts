import { http, HttpResponse, delay } from 'msw'
import type { Reminder } from '@/lib/schemas/reminder.schema'
import { ReminderSchema, UpdateReminderRequestSchema } from '@/lib/schemas/reminder.schema'
import { remindersFixture } from '../data/reminders.fixture'

// In-memory storage (will be replaced with MSW database pattern)
let reminders: Reminder[] = [...remindersFixture]

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Helper: Generate UUID
const generateUUID = () => crypto.randomUUID()

// GET /api/reminders - List all reminders with filters
export const getRemindersHandler = http.get('/api/reminders', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const taskId = url.searchParams.get('taskId')
  const fired = url.searchParams.get('fired')

  let filtered = reminders

  if (taskId) {
    filtered = filtered.filter(r => r.task_id === taskId)
  }

  if (fired === 'true') {
    filtered = filtered.filter(r => r.fired)
  } else if (fired === 'false') {
    filtered = filtered.filter(r => !r.fired)
  }

  return HttpResponse.json({ reminders: filtered }, { status: 200 })
})

// GET /api/reminders/:id - Get single reminder
export const getReminderHandler = http.get('/api/reminders/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const reminder = reminders.find(r => r.id === id)

  if (!reminder) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Reminder not found' } },
      { status: 404 }
    )
  }

  return HttpResponse.json(reminder, { status: 200 })
})

// POST /api/reminders - Create new reminder
export const createReminderHandler = http.post('/api/reminders', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    const now = new Date().toISOString()
    const newReminder: Reminder = {
      id: generateUUID(),
      ...(body as any),
      createdAt: now,
      fired: false,
    }

    ReminderSchema.parse(newReminder)
    reminders.push(newReminder)

    return HttpResponse.json(newReminder, { status: 201 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid reminder data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// PATCH /api/reminders/:id - Update reminder
export const updateReminderHandler = http.patch('/api/reminders/:id', async ({ params, request }) => {
  await simulateLatency()

  const { id } = params
  const body = await request.json()
  const reminderIndex = reminders.findIndex(r => r.id === id)

  if (reminderIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Reminder not found' } },
      { status: 404 }
    )
  }

  try {
    UpdateReminderRequestSchema.parse(body)

    const reminder = reminders[reminderIndex]
    const updatedReminder: Reminder = {
      ...reminder,
      ...(body as any),
    }

    reminders[reminderIndex] = updatedReminder

    return HttpResponse.json(updatedReminder, { status: 200 })
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

// DELETE /api/reminders/:id - Hard delete reminder
export const deleteReminderHandler = http.delete('/api/reminders/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const reminderIndex = reminders.findIndex(r => r.id === id)

  if (reminderIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Reminder not found' } },
      { status: 404 }
    )
  }

  reminders.splice(reminderIndex, 1)
  return HttpResponse.json(null, { status: 204 })
})

// POST /api/reminders/:id/fired - Mark reminder as fired
export const markReminderDeliveredHandler = http.post(
  '/api/reminders/:id/fired',
  async ({ params }) => {
    await simulateLatency()

    const { id } = params
    const reminderIndex = reminders.findIndex(r => r.id === id)

    if (reminderIndex === -1) {
      return HttpResponse.json(
        { error: { code: 'RESOURCE_NOT_FOUND', message: 'Reminder not found' } },
        { status: 404 }
      )
    }

    reminders[reminderIndex].fired = true

    return HttpResponse.json(reminders[reminderIndex], { status: 200 })
  }
)

// Export all reminder handlers
export const remindersHandlers = [
  getRemindersHandler,
  getReminderHandler,
  createReminderHandler,
  updateReminderHandler,
  deleteReminderHandler,
  markReminderDeliveredHandler,
]
