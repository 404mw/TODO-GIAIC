'use client'

import { useState } from 'react'
import { format } from 'date-fns'
import type { Note } from '@/lib/schemas/note.schema'
import { useUpdateNote, useDeleteNote } from '@/lib/hooks/useNotes'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { ConvertNoteDrawer } from './ConvertNoteDrawer'

interface NoteCardProps {
  note: Note
  onEdit?: (note: Note) => void
}

export function NoteCard({ note, onEdit }: NoteCardProps) {
  const { toast } = useToast()
  const updateNote = useUpdateNote()
  const deleteNote = useDeleteNote()
  const [isDeleting, setIsDeleting] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [showConvertDrawer, setShowConvertDrawer] = useState(false) // T130, T132

  const handleArchive = async () => {
    try {
      await updateNote.mutateAsync({
        id: note.id,
        input: { archived: !note.archived },
      })

      toast({
        title: note.archived ? 'Note restored' : 'Note archived',
        description: note.archived
          ? 'Note has been restored to your notes'
          : 'Note has been archived',
        variant: 'success',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to archive note',
        variant: 'error',
      })
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to permanently delete this note?')) {
      return
    }

    setIsDeleting(true)

    try {
      await deleteNote.mutateAsync(note.id)

      toast({
        title: 'Note deleted',
        description: 'Note has been permanently deleted',
        variant: 'success',
      })
    } catch (error) {
      setIsDeleting(false)
      toast({
        title: 'Error',
        description: 'Failed to delete note',
        variant: 'error',
      })
    }
  }

  // Truncate content for preview
  const shouldTruncate = note.content.length > 200 && !isExpanded
  const displayContent = shouldTruncate
    ? note.content.slice(0, 200) + '...'
    : note.content

  return (
    <div className="group rounded-lg border border-gray-200 bg-white p-4 transition-all hover:border-gray-300 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700">
      {/* Content */}
      <div className="mb-3">
        <p className="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
          {displayContent}
        </p>
        {note.content.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>

      {/* Voice indicator */}
      {note.voiceUrl && (
        <div className="mb-3 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
          <span>Voice note ({note.voiceDurationSeconds}s)</span>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {format(new Date(note.updatedAt), 'MMM d, yyyy HH:mm')}
        </span>

        <div className="flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100">
          {/* T130, T132: Convert to Task button */}
          {!note.archived && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowConvertDrawer(true)}
              className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              <svg
                className="mr-1 h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              Task
            </Button>
          )}
          {onEdit && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(note)}
            >
              Edit
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleArchive}
            disabled={updateNote.isPending}
          >
            {note.archived ? 'Restore' : 'Archive'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
          >
            Delete
          </Button>
        </div>
      </div>

      {/* T130, T132: Convert Note Drawer */}
      <ConvertNoteDrawer
        note={note}
        isOpen={showConvertDrawer}
        onClose={() => setShowConvertDrawer(false)}
      />
    </div>
  )
}
