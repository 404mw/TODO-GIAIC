'use client'

import { useState } from 'react'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useNotes } from '@/lib/hooks/useNotes'
import { NoteList } from '@/components/notes/NoteList'
import { NoteEditor } from '@/components/notes/NoteEditor'
import type { Note } from '@/lib/schemas/note.schema'

/**
 * Archived Notes management page
 *
 * Displays all archived notes with options to:
 * - Edit: Modify note content
 * - Unarchive: Restore note to active notes
 */

export default function ArchivedNotesPage() {
  const [editingNote, setEditingNote] = useState<Note | null>(null)

  const {
    data: notesResponse,
    isLoading,
    error,
  } = useNotes()

  // Unwrap API response and filter for archived notes only
  const allNotes = notesResponse?.data || []
  const notes = allNotes.filter((note: Note) => note.archived)

  const handleEdit = (note: Note) => {
    setEditingNote(note)
  }

  const handleCancel = () => {
    setEditingNote(null)
  }

  const handleSuccess = () => {
    setEditingNote(null)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard/settings"
            className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Archived Notes
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage notes you've archived
            </p>
          </div>
        </div>

        {/* Edit form */}
        {editingNote && (
          <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Edit Note
            </h2>
            <NoteEditor
              note={editingNote}
              onSuccess={handleSuccess}
              onCancel={handleCancel}
            />
          </div>
        )}

        {/* Content */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
          </div>
        ) : error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200">
            <p className="font-medium">Failed to load archived notes</p>
            <p className="text-sm">Please try refreshing the page.</p>
          </div>
        ) : notes.length === 0 ? (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-gray-900">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
              />
            </svg>
            <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
              No archived notes
            </h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Notes you archive will appear here for you to restore or manage.
            </p>
            <Link href="/dashboard/notes" className="mt-4 inline-block">
              <button className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                View Active Notes
              </button>
            </Link>
          </div>
        ) : (
          <NoteList
            notes={notes}
            isLoading={isLoading}
            error={error}
            onEdit={handleEdit}
          />
        )}
      </div>
    </DashboardLayout>
  )
}
