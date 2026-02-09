import { http, HttpResponse, delay } from 'msw'
import type { Note } from '@/lib/schemas/note.schema'
import { NoteSchema, UpdateNoteRequestSchema } from '@/lib/schemas/note.schema'
import { notesFixture } from '../data/notes.fixture'

// In-memory storage (will be replaced with MSW database pattern)
let notes: Note[] = [...notesFixture]

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Helper: Generate UUID
const generateUUID = () => crypto.randomUUID()

// GET /api/notes - List all notes with filters
export const getNotesHandler = http.get('/api/notes', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const archived = url.searchParams.get('archived')

  let filtered = notes

  if (archived === 'true') {
    filtered = filtered.filter(n => n.archived)
  } else if (archived === 'false') {
    filtered = filtered.filter(n => !n.archived)
  }

  // Sort by most recent first
  filtered = filtered.sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  return HttpResponse.json(filtered, { status: 200 })
})

// GET /api/notes/:id - Get single note
export const getNoteHandler = http.get('/api/notes/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const note = notes.find(n => n.id === id)

  if (!note) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Note not found' } },
      { status: 404 }
    )
  }

  return HttpResponse.json(note, { status: 200 })
})

// POST /api/notes - Create new note
export const createNoteHandler = http.post('/api/notes', async ({ request }) => {
  await simulateLatency()

  const body = await request.json()

  try {
    const now = new Date().toISOString()
    const newNote: Note = {
      id: generateUUID(),
      ...(body as any),
      createdAt: now,
      updated_at: now,
      archived: false,
    }

    NoteSchema.parse(newNote)
    notes.push(newNote)

    return HttpResponse.json(newNote, { status: 201 })
  } catch (error) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid note data',
          details: error,
        },
      },
      { status: 400 }
    )
  }
})

// PATCH /api/notes/:id - Update note
export const updateNoteHandler = http.patch('/api/notes/:id', async ({ params, request }) => {
  await simulateLatency()

  const { id } = params
  const body = await request.json()
  const noteIndex = notes.findIndex(n => n.id === id)

  if (noteIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Note not found' } },
      { status: 404 }
    )
  }

  try {
    UpdateNoteRequestSchema.parse(body)

    const note = notes[noteIndex]
    const updatedNote: Note = {
      ...note,
      ...(body as any),
      updated_at: new Date().toISOString(),
    }

    notes[noteIndex] = updatedNote

    return HttpResponse.json(updatedNote, { status: 200 })
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

// DELETE /api/notes/:id - Soft delete note (set archived=true)
export const deleteNoteHandler = http.delete('/api/notes/:id', async ({ params }) => {
  await simulateLatency()

  const { id } = params
  const noteIndex = notes.findIndex(n => n.id === id)

  if (noteIndex === -1) {
    return HttpResponse.json(
      { error: { code: 'RESOURCE_NOT_FOUND', message: 'Note not found' } },
      { status: 404 }
    )
  }

  notes[noteIndex].archived = true
  notes[noteIndex].updated_at = new Date().toISOString()

  return HttpResponse.json(null, { status: 204 })
})

// Export all note handlers
export const notesHandlers = [
  getNotesHandler,
  getNoteHandler,
  createNoteHandler,
  updateNoteHandler,
  deleteNoteHandler,
]
