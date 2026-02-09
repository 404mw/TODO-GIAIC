import { http, HttpResponse, delay } from 'msw'

// Minimal type definition for AI interaction log (schema file doesn't exist yet)
interface AIInteractionLog {
  id: string
  timestamp: string
  actor: 'user' | 'ai'
  task_id?: string
  noteId?: string
  requestType?: string
  [key: string]: any
}

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// In-memory storage for AI interaction logs
let aiLogs: AIInteractionLog[] = []

// POST /api/ai/parse-note - Parse note into structured task (DISABLED)
export const parseNoteHandler = http.post('/api/ai/parse-note', async () => {
  await simulateLatency()

  return HttpResponse.json(
    {
      error: {
        code: 'FEATURE_DISABLED',
        message: 'AI features are currently disabled. This feature will be enabled in a future release.',
      },
    },
    { status: 503 }
  )
})

// POST /api/ai/generate-subtasks - Generate subtasks from task (DISABLED)
export const generateSubtasksHandler = http.post('/api/ai/generate-subtasks', async () => {
  await simulateLatency()

  return HttpResponse.json(
    {
      error: {
        code: 'FEATURE_DISABLED',
        message: 'AI features are currently disabled. This feature will be enabled in a future release.',
      },
    },
    { status: 503 }
  )
})

// GET /api/ai/logs - Get AI interaction logs
export const getAILogsHandler = http.get('/api/ai/logs', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const taskId = url.searchParams.get('taskId')
  const noteId = url.searchParams.get('noteId')
  const requestType = url.searchParams.get('requestType')

  let filtered = aiLogs

  if (taskId) {
    filtered = filtered.filter(log => log.task_id === taskId)
  }

  if (noteId) {
    filtered = filtered.filter(log => log.noteId === noteId)
  }

  if (requestType) {
    filtered = filtered.filter(log => log.requestType === requestType)
  }

  // Sort by most recent first
  filtered = filtered.sort((a, b) =>
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )

  return HttpResponse.json(filtered, { status: 200 })
})

// POST /api/ai/logs - Create AI interaction log
export const createAILogHandler = http.post('/api/ai/logs', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    const newLog: AIInteractionLog = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      actor: 'ai',
      ...(body as any),
    }

    aiLogs.push(newLog)

    return HttpResponse.json(newLog, { status: 201 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid AI log data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// Export all AI handlers
export const aiHandlers = [
  parseNoteHandler,
  generateSubtasksHandler,
  getAILogsHandler,
  createAILogHandler,
]
