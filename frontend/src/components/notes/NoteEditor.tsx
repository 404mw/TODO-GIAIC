'use client'

import { useState, useEffect } from 'react'
import type { Note } from '@/lib/schemas/note.schema'
import { useCreateNote, useUpdateNote } from '@/lib/hooks/useNotes'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'

interface NoteEditorProps {
  note?: Note
  onSuccess?: () => void
  onCancel?: () => void
}

export function NoteEditor({ note, onSuccess, onCancel }: NoteEditorProps) {
  const { toast } = useToast()
  const createNote = useCreateNote()
  const updateNote = useUpdateNote()

  const isEditing = !!note
  const [content, setContent] = useState(note?.content || '')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!content.trim()) {
      toast({
        title: 'Error',
        message: 'Note content cannot be empty',
        type: 'error',
      })
      return
    }

    setIsSubmitting(true)

    try {
      if (isEditing) {
        await updateNote.mutateAsync({
          id: note.id,
          content: content.trim(),
        })

        toast({
          title: 'Note updated',
          message: 'Your note has been saved',
          type: 'success',
        })
      } else {
        await createNote.mutateAsync({ content: content.trim() })

        toast({
          title: 'Note created',
          message: 'Your new note has been added',
          type: 'success',
        })

        setContent('')
      }

      onSuccess?.()
    } catch (error) {
      toast({
        title: 'Error',
        message: isEditing ? 'Failed to update note' : 'Failed to create note',
        type: 'error',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Calculate character count
  const charCount = content.length
  const maxChars = 2000 // MAX_NOTE_CHARS_HARD

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your note..."
          rows={6}
          maxLength={maxChars}
          className="resize-none"
          autoFocus
        />
        <div className="mt-1 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>{charCount}/{maxChars} characters</span>
          {charCount > maxChars * 0.9 && (
            <span className="text-yellow-600 dark:text-yellow-400">
              Approaching limit
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-2">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        )}
        <Button
          type="submit"
          disabled={isSubmitting || !content.trim()}
          className="flex-1"
        >
          {isSubmitting
            ? isEditing
              ? 'Saving...'
              : 'Creating...'
            : isEditing
            ? 'Save Note'
            : 'Create Note'}
        </Button>
      </div>
    </form>
  )
}
