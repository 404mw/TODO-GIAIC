'use client'

import type { Note } from '@/lib/schemas/note.schema'
import { NoteCard } from './NoteCard'

interface NoteListProps {
  notes: Note[]
  isLoading?: boolean
  error?: Error | null
  onEdit?: (note: Note) => void
}

export function NoteList({ notes, isLoading, error, onEdit }: NoteListProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="h-40 animate-pulse rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-800 dark:bg-gray-800"
          />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="py-12 text-center">
        <p className="text-red-500 dark:text-red-400">
          Error loading notes: {error.message}
        </p>
      </div>
    )
  }

  if (notes.length === 0) {
    return (
      <div className="py-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
          No notes yet
        </h3>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          Start capturing your thoughts by creating a new note.
        </p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {notes.map((note) => (
        <NoteCard key={note.id} note={note} onEdit={onEdit} />
      ))}
    </div>
  )
}
