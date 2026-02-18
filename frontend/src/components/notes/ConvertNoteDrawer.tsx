/**
 * ConvertNoteDrawer Component (T130, T132)
 * Phase 8 - US5 Quick Notes
 *
 * Allows users to convert a note into a task.
 * Currently disabled until backend AI integration is complete.
 */

'use client'

import { useState } from 'react'
import type { Note } from '@/lib/schemas/note.schema'
import { useCreateTask } from '@/lib/hooks/useTasks'
import { useArchiveNote } from '@/lib/hooks/useNotes'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Label } from '@/components/ui/Label'

interface ConvertNoteDrawerProps {
  note: Note
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export function ConvertNoteDrawer({
  note,
  isOpen,
  onClose,
  onSuccess,
}: ConvertNoteDrawerProps) {
  const { toast } = useToast()
  const createTask = useCreateTask()
  const archiveNote = useArchiveNote()

  // Pre-fill title from first line of note, description from rest
  const lines = note.content.split('\n').filter(line => line.trim())
  const defaultTitle = lines[0]?.slice(0, 100) || 'Untitled Task'
  const defaultDescription = lines.slice(1).join('\n').trim()

  const [title, setTitle] = useState(defaultTitle)
  const [description, setDescription] = useState(defaultDescription)
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [archiveAfterConvert, setArchiveAfterConvert] = useState(true)
  const [isConverting, setIsConverting] = useState(false)

  // AI features disabled until backend ready
  const aiEnabled = false

  const handleConvert = async () => {
    if (!title.trim()) {
      toast({
        title: 'Error',
        message: 'Task title cannot be empty',
        type: 'error',
      })
      return
    }

    setIsConverting(true)

    try {
      // Create the task
      await createTask.mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
      })

      // Optionally archive the note
      if (archiveAfterConvert) {
        await archiveNote.mutateAsync({ id: note.id })
      }

      toast({
        title: 'Note converted',
        message: 'Your note has been converted to a task',
        type: 'success',
      })

      onSuccess?.()
      onClose()
    } catch (error) {
      toast({
        title: 'Error',
        message: 'Failed to convert note to task',
        type: 'error',
      })
    } finally {
      setIsConverting(false)
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto bg-white p-6 shadow-xl dark:bg-gray-900 sm:max-w-lg">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Convert to Task
          </h2>
          <button
            onClick={onClose}
            className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Original note preview */}
        <div className="mb-6 rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Original Note
          </h3>
          <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-4">
            {note.content}
          </p>
        </div>

        {/* AI-powered conversion (disabled) */}
        {!aiEnabled && (
          <div className="mb-6 rounded-lg border border-dashed border-gray-300 p-4 dark:border-gray-600">
            <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span className="text-sm">
                AI-powered conversion coming soon
              </span>
            </div>
            <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
              Smart title extraction and task suggestions will be available after backend integration.
            </p>
          </div>
        )}

        {/* Manual conversion form */}
        <form onSubmit={(e) => { e.preventDefault(); handleConvert(); }} className="space-y-4">
          <div>
            <Label htmlFor="task-title">Task Title</Label>
            <Input
              id="task-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              className="mt-1"
              autoFocus
            />
          </div>

          <div>
            <Label htmlFor="task-description">Description (optional)</Label>
            <Textarea
              id="task-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add more details..."
              rows={4}
              className="mt-1"
            />
          </div>

          <div>
            <Label>Priority</Label>
            <div className="mt-2 flex gap-2">
              {(['low', 'medium', 'high'] as const).map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPriority(p)}
                  className={[
                    'rounded-md px-4 py-2 text-sm font-medium capitalize transition-colors',
                    priority === p
                      ? p === 'high'
                        ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                        : p === 'medium'
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                        : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
                  ].join(' ')}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              id="archive-note"
              type="checkbox"
              checked={archiveAfterConvert}
              onChange={(e) => setArchiveAfterConvert(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
            />
            <Label htmlFor="archive-note" className="text-sm">
              Archive note after conversion
            </Label>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isConverting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isConverting || !title.trim()}
              className="flex-1"
            >
              {isConverting ? 'Converting...' : 'Convert to Task'}
            </Button>
          </div>
        </form>
      </div>
    </>
  )
}
