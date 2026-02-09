'use client'

import { useState } from 'react'
import { useNotes } from '@/lib/hooks/useNotes'
import type { Note } from '@/lib/schemas/note.schema'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { NoteList } from '@/components/notes/NoteList'
import { NoteEditor } from '@/components/notes/NoteEditor'
import { Button } from '@/components/ui/Button'

export default function NotesPage() {
  const [showArchived, setShowArchived] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [editingNote, setEditingNote] = useState<Note | null>(null)

  const {
    data: notesResponse,
    isLoading,
    error,
  } = useNotes()

  // Unwrap API response and filter based on archived state
  const allNotes = notesResponse?.data || []
  const notes = allNotes.filter((note: Note) => note.archived === showArchived)

  const handleEdit = (note: Note) => {
    setEditingNote(note)
    setIsCreating(false)
  }

  const handleCancel = () => {
    setIsCreating(false)
    setEditingNote(null)
  }

  const handleSuccess = () => {
    setIsCreating(false)
    setEditingNote(null)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Notes
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Quick capture for thoughts, ideas, and reminders
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowArchived(!showArchived)}
            >
              {showArchived ? 'Show Active' : 'Show Archived'}
            </Button>
            {!isCreating && !editingNote && (
              <Button onClick={() => setIsCreating(true)}>
                New Note
              </Button>
            )}
          </div>
        </div>

        {/* Create/Edit form */}
        {(isCreating || editingNote) && (
          <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              {editingNote ? 'Edit Note' : 'New Note'}
            </h2>
            <NoteEditor
              note={editingNote || undefined}
              onSuccess={handleSuccess}
              onCancel={handleCancel}
            />
          </div>
        )}

        {/* Notes grid */}
        <NoteList
          notes={notes}
          isLoading={isLoading}
          error={error}
          onEdit={handleEdit}
        />
      </div>
    </DashboardLayout>
  )
}
