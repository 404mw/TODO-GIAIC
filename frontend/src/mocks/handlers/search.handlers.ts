import { http, HttpResponse, delay } from 'msw'
import Fuse from 'fuse.js'
import type { Task } from '@/lib/schemas/task.schema'
import type { Subtask } from '@/lib/schemas/subtask.schema'
import type { Note } from '@/lib/schemas/note.schema'
import { tasksFixture } from '../data/tasks.fixture'
import { subtasksFixture } from '../data/subtasks.fixture'
import { notesFixture } from '../data/notes.fixture'

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Search result types
interface TaskSearchResult {
  type: 'task'
  item: Task
  score: number
  matches: Array<{ key: string; value: string; indices: readonly [number, number][] }>
}

interface SubtaskSearchResult {
  type: 'subtask'
  item: Subtask
  score: number
  matches: Array<{ key: string; value: string; indices: readonly [number, number][] }>
}

interface NoteSearchResult {
  type: 'note'
  item: Note
  score: number
  matches: Array<{ key: string; value: string; indices: readonly [number, number][] }>
}

type SearchResult = TaskSearchResult | SubtaskSearchResult | NoteSearchResult

interface GroupedSearchResults {
  tasks: TaskSearchResult[]
  subtasks: SubtaskSearchResult[]
  notes: NoteSearchResult[]
  totalResults: number
}

// Fuse.js configuration for tasks
const tasksFuseOptions: any = {
  keys: [
    { name: 'title', weight: 2 },
    { name: 'description', weight: 1.5 },
    { name: 'tags', weight: 1 },
  ],
  includeScore: true,
  includeMatches: true,
  threshold: 0.4, // Lower = stricter matching
  minMatchCharLength: 2,
}

// Fuse.js configuration for subtasks
const subtasksFuseOptions: any = {
  keys: [{ name: 'title', weight: 2 }],
  includeScore: true,
  includeMatches: true,
  threshold: 0.4,
  minMatchCharLength: 2,
}

// Fuse.js configuration for notes
const notesFuseOptions: any = {
  keys: [{ name: 'content', weight: 2 }],
  includeScore: true,
  includeMatches: true,
  threshold: 0.4,
  minMatchCharLength: 2,
}

// GET /api/search - Universal search across tasks, subtasks, and notes
export const searchHandler = http.get('/api/search', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const query = url.searchParams.get('q')
  const limit = parseInt(url.searchParams.get('limit') || '20', 10)

  if (!query || query.trim().length < 2) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Search query must be at least 2 characters',
        },
      },
      { status: 400 }
    )
  }

  // Initialize Fuse instances with current data
  const tasksFuse = new Fuse(tasksFixture.filter(t => !t.hidden), tasksFuseOptions)
  const subtasksFuse = new Fuse(subtasksFixture, subtasksFuseOptions)
  const notesFuse = new Fuse(notesFixture.filter(n => !n.archived), notesFuseOptions)

  // Perform searches
  const tasksResults = tasksFuse.search(query).map(
    (result): TaskSearchResult => ({
      type: 'task',
      item: result.item,
      score: result.score || 0,
      matches:
        result.matches?.map(m => ({
          key: m.key || '',
          value: m.value || '',
          indices: m.indices || [],
        })) || [],
    })
  )

  const subtasksResults = subtasksFuse.search(query).map(
    (result): SubtaskSearchResult => ({
      type: 'subtask',
      item: result.item,
      score: result.score || 0,
      matches:
        result.matches?.map(m => ({
          key: m.key || '',
          value: m.value || '',
          indices: m.indices || [],
        })) || [],
    })
  )

  const notesResults = notesFuse.search(query).map(
    (result): NoteSearchResult => ({
      type: 'note',
      item: result.item,
      score: result.score || 0,
      matches:
        result.matches?.map(m => ({
          key: m.key || '',
          value: m.value || '',
          indices: m.indices || [],
        })) || [],
    })
  )

  // Combine and sort by score (lower score = better match)
  const allResults: SearchResult[] = [
    ...tasksResults,
    ...subtasksResults,
    ...notesResults,
  ].sort((a, b) => a.score - b.score)

  // Apply limit across all results
  const limitedResults = allResults.slice(0, limit)

  // Group results by type
  const groupedResults: GroupedSearchResults = {
    tasks: limitedResults.filter(r => r.type === 'task') as TaskSearchResult[],
    subtasks: limitedResults.filter(r => r.type === 'subtask') as SubtaskSearchResult[],
    notes: limitedResults.filter(r => r.type === 'note') as NoteSearchResult[],
    totalResults: allResults.length,
  }

  return HttpResponse.json(groupedResults, { status: 200 })
})

// GET /api/search/tasks - Search tasks only
export const searchTasksHandler = http.get('/api/search/tasks', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const query = url.searchParams.get('q')
  const limit = parseInt(url.searchParams.get('limit') || '10', 10)

  if (!query || query.trim().length < 2) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Search query must be at least 2 characters',
        },
      },
      { status: 400 }
    )
  }

  const tasksFuse = new Fuse(tasksFixture.filter(t => !t.hidden), tasksFuseOptions)
  const results = tasksFuse.search(query, { limit })

  return HttpResponse.json(
    results.map(r => ({
      item: r.item,
      score: r.score,
      matches: r.matches,
    })),
    { status: 200 }
  )
})

// GET /api/search/notes - Search notes only
export const searchNotesHandler = http.get('/api/search/notes', async ({ request }) => {
  await simulateLatency()

  const url = new URL(request.url)
  const query = url.searchParams.get('q')
  const limit = parseInt(url.searchParams.get('limit') || '10', 10)

  if (!query || query.trim().length < 2) {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Search query must be at least 2 characters',
        },
      },
      { status: 400 }
    )
  }

  const notesFuse = new Fuse(notesFixture.filter(n => !n.archived), notesFuseOptions)
  const results = notesFuse.search(query, { limit })

  return HttpResponse.json(
    results.map(r => ({
      item: r.item,
      score: r.score,
      matches: r.matches,
    })),
    { status: 200 }
  )
})

// Export all search handlers
export const searchHandlers = [searchHandler, searchTasksHandler, searchNotesHandler]
