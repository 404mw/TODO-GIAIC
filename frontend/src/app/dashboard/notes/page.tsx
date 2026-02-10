'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { useNotes } from '@/lib/hooks/useNotes'
import type { Note } from '@/lib/schemas/note.schema'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { NoteList } from '@/components/notes/NoteList'
import { NoteEditor } from '@/components/notes/NoteEditor'
import { Button } from '@/components/ui/Button'

function NotesPageContent() {
  const searchParams = useSearchParams()
  const [isCreating, setIsCreating] = useState(false)
  const [editingNote, setEditingNote] = useState<Note | null>(null)

  // Handle ?create=true query parameter
  useEffect(() => {
    if (searchParams.get('create') === 'true') {
      setIsCreating(true)
      setEditingNote(null)
    }
  }, [searchParams])

  const {
    data: notesResponse,
    isLoading,
    error,
  } = useNotes()

  // Unwrap API response and filter for active notes only
  const allNotes = notesResponse?.data || []
  const notes = allNotes.filter((note: Note) => !note.archived)

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
          {!isCreating && !editingNote && (
            <Button onClick={() => setIsCreating(true)}>
              New Note
            </Button>
          )}
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

export default function NotesPage() {
  return (
    <Suspense fallback={
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
        </div>
      </DashboardLayout>
    }>
      <NotesPageContent />
    </Suspense>
  )
}
