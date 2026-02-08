'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Note, NoteCreate, NoteUpdate } from '@/lib/schemas/note.schema'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/Dialog'
import { useCreateNote, useUpdateNote } from '@/lib/hooks/useNotes'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Label } from '@/components/ui/Label'
import { Textarea } from '@/components/ui/Textarea'
import { LIMITS } from '@/lib/config/limits'

interface NewNoteModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  editNote?: Note | null
}

/**
 * NewNoteModal Component
 *
 * A modal dialog for creating and editing notes with:
 * - Content (required, textarea)
 * - Character count indicator
 * - Soft warning at 750 chars, hard limit at 1000 chars
 */
export function NewNoteModal({ open, onOpenChange, editNote }: NewNoteModalProps) {
  const router = useRouter()
  const { toast } = useToast()
  const createNote = useCreateNote()
  const updateNote = useUpdateNote()

  const isEditMode = !!editNote

  // Form state
  const [content, setContent] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Character count indicators
  const charCount = content.length
  const isNearLimit = charCount >= LIMITS.MAX_NOTE_CHARS_SOFT
  const isAtLimit = charCount >= LIMITS.MAX_NOTE_CHARS_HARD

  // Prefill form when editing
  useEffect(() => {
    if (editNote) {
      setContent(editNote.content)
    }
  }, [editNote])

  const resetForm = () => {
    setContent('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!content.trim()) {
      toast({
        title: 'Error',
        description: 'Note content is required',
        variant: 'error',
      })
      return
    }

    if (content.length > LIMITS.MAX_NOTE_CHARS_HARD) {
      toast({
        title: 'Error',
        description: `Note content must be less than ${LIMITS.MAX_NOTE_CHARS_HARD} characters`,
        variant: 'error',
      })
      return
    }

    setIsSubmitting(true)

    try {
      if (isEditMode && editNote) {
        // Update existing note
        const updateData: NoteUpdate = {
          content: content.trim(),
        }

        await updateNote.mutateAsync({ id: editNote.id, input: updateData })

        toast({
          title: 'Note updated',
          description: 'Your changes have been saved',
          variant: 'success',
        })

        resetForm()
        onOpenChange(false)
      } else {
        // Create new note
        const createData: NoteCreate = {
          content: content.trim(),
        }

        const newNote = await createNote.mutateAsync(createData)

        toast({
          title: 'Note created',
          description: 'Your new note has been added',
          variant: 'success',
        })

        resetForm()
        onOpenChange(false)

        // Navigate to the notes page
        router.push('/dashboard/notes')
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: isEditMode ? 'Failed to update note' : 'Failed to create note',
        variant: 'error',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetForm()
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditMode ? 'Edit Note' : 'Create New Note'}</DialogTitle>
          <DialogDescription>
            {isEditMode
              ? 'Update your note content below.'
              : 'Capture a quick note. You can convert it to a task later.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Content */}
          <div>
            <Label htmlFor="modal-content">
              Content <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="modal-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What's on your mind?"
              rows={8}
              maxLength={LIMITS.MAX_NOTE_CHARS_HARD}
              required
              autoFocus
              className="mt-1"
            />
            <div className="mt-1 flex items-center justify-between text-xs">
              <span
                className={`${
                  isAtLimit
                    ? 'font-semibold text-red-600 dark:text-red-400'
                    : isNearLimit
                      ? 'font-medium text-orange-600 dark:text-orange-400'
                      : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {charCount}/{LIMITS.MAX_NOTE_CHARS_HARD} characters
              </span>
              {isNearLimit && !isAtLimit && (
                <span className="text-orange-600 dark:text-orange-400">
                  Approaching limit
                </span>
              )}
              {isAtLimit && (
                <span className="font-semibold text-red-600 dark:text-red-400">
                  Character limit reached
                </span>
              )}
            </div>
          </div>

          {/* Info tip */}
          <div className="rounded-md border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              💡 <strong>Tip:</strong> Use notes for quick thoughts or reminders. You can
              convert notes to tasks with AI-powered suggestions from the Notes page.
            </p>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 border-t border-gray-200 pt-4 dark:border-gray-800">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || !content.trim()}>
              {isSubmitting
                ? isEditMode
                  ? 'Saving...'
                  : 'Creating...'
                : isEditMode
                  ? 'Save Changes'
                  : 'Create Note'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
