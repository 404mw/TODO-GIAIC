'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Recurrence, Task, TaskCreate, TaskUpdate } from '@/lib/schemas/task.schema'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/Dialog'
import { useCreateTask, useUpdateTask } from '@/lib/hooks/useTasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Textarea } from '@/components/ui/Textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'
import { RecurrenceEditor } from '@/components/recurrence/RecurrenceEditor'
import { RecurrencePreview } from '@/components/recurrence/RecurrencePreview'

interface NewTaskModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  editTask?: Task | null
}

/**
 * NewTaskModal Component
 *
 * A modal dialog for creating and editing tasks with all fields:
 * - Title, Description, Priority, Due Date
 * - Tags
 * - Estimated Duration
 * - Recurrence settings
 */
export function NewTaskModal({ open, onOpenChange, editTask }: NewTaskModalProps) {
  const router = useRouter()
  const { toast } = useToast()
  const createTask = useCreateTask()
  const updateTask = useUpdateTask()

  const isEditMode = !!editTask

  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [dueDate, setDueDate] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [estimatedDuration, setEstimatedDuration] = useState('')
  const [recurrence, setRecurrence] = useState<Recurrence | undefined>()
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Prefill form when editing
  useEffect(() => {
    if (editTask) {
      setTitle(editTask.title)
      setDescription(editTask.description || '')
      setPriority(editTask.priority)
      setTags(editTask.tags || [])
      setEstimatedDuration(editTask.estimatedDuration?.toString() || '')
      setRecurrence(editTask.recurrence || undefined)
      // Format dueDate for datetime-local input
      if (editTask.dueDate) {
        const date = new Date(editTask.dueDate)
        const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
        setDueDate(localDate.toISOString().slice(0, 16))
      } else {
        setDueDate('')
      }
    }
  }, [editTask])

  const resetForm = () => {
    setTitle('')
    setDescription('')
    setPriority('medium')
    setDueDate('')
    setTags([])
    setTagInput('')
    setEstimatedDuration('')
    setRecurrence(undefined)
  }

  const handleAddTag = () => {
    const tag = tagInput.trim()
    if (tag && !tags.includes(tag) && tags.length < 20) {
      setTags([...tags, tag])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove))
  }

  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      toast({
        title: 'Error',
        description: 'Task title is required',
        variant: 'error',
      })
      return
    }

    setIsSubmitting(true)

    try {
      if (isEditMode && editTask) {
        // Update existing task
        const updateData: TaskUpdate = {
          version: editTask.version,
          title: title.trim(),
          description: description.trim() || undefined,
          priority,
          tags,
          dueDate: dueDate ? new Date(dueDate).toISOString() : null,
          estimatedDuration: estimatedDuration
            ? parseInt(estimatedDuration, 10)
            : undefined,
          recurrence,
        }

        await updateTask.mutateAsync({ id: editTask.id, input: updateData })

        toast({
          title: 'Task updated',
          description: 'Your changes have been saved',
          variant: 'success',
        })

        resetForm()
        onOpenChange(false)
      } else {
        // Create new task
        const createData: TaskCreate = {
          title: title.trim(),
          description: description.trim() || undefined,
          priority,
          tags,
          dueDate: dueDate ? new Date(dueDate).toISOString() : null,
          estimatedDuration: estimatedDuration
            ? parseInt(estimatedDuration, 10)
            : undefined,
          recurrence,
        }

        const newTask = await createTask.mutateAsync(createData)

        toast({
          title: 'Task created',
          description: 'Your new task has been added',
          variant: 'success',
        })

        resetForm()
        onOpenChange(false)

        // Navigate to the new task detail page
        router.push(`/dashboard/tasks/${newTask.id}`)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: isEditMode ? 'Failed to update task' : 'Failed to create task',
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
          <DialogTitle>{isEditMode ? 'Edit Task' : 'Create New Task'}</DialogTitle>
          <DialogDescription>
            {isEditMode
              ? 'Update the task details below.'
              : 'Add a new task to your list. Fill in the details below.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Title */}
          <div>
            <Label htmlFor="modal-title">
              Title <span className="text-red-500">*</span>
            </Label>
            <Input
              id="modal-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What needs to be done?"
              maxLength={200}
              required
              autoFocus
              className="mt-1"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {title.length}/200 characters
            </p>
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="modal-description">Description</Label>
            <Textarea
              id="modal-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add more details (optional)"
              rows={2}
              maxLength={1000}
              className="mt-1"
            />
          </div>

          {/* Priority and Due Date Row */}
          <div className="grid gap-4 sm:grid-cols-2">
            {/* Priority */}
            <div>
              <Label htmlFor="modal-priority">Priority</Label>
              <Select
                value={priority}
                onValueChange={(value) =>
                  setPriority(value as 'low' | 'medium' | 'high')
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Due Date */}
            <div>
              <Label htmlFor="modal-dueDate">Due Date</Label>
              <Input
                id="modal-dueDate"
                type="datetime-local"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Tags */}
          <div>
            <Label htmlFor="modal-tags">Tags</Label>
            <div className="mt-1 flex gap-2">
              <Input
                id="modal-tags"
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagInputKeyDown}
                placeholder="Add a tag..."
                maxLength={30}
                disabled={tags.length >= 20}
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddTag}
                disabled={!tagInput.trim() || tags.length >= 20}
              >
                Add
              </Button>
            </div>
            {tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-blue-600 dark:hover:text-blue-300"
                    >
                      <svg
                        className="h-3 w-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            )}
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {tags.length}/20 tags
            </p>
          </div>

          {/* Estimated Duration */}
          <div>
            <Label htmlFor="modal-duration">Estimated Duration (minutes)</Label>
            <Input
              id="modal-duration"
              type="number"
              value={estimatedDuration}
              onChange={(e) => setEstimatedDuration(e.target.value)}
              placeholder="How long will this take?"
              min="1"
              max="720"
              className="mt-1"
            />
          </div>

          {/* Recurrence */}
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-800 dark:bg-gray-900">
            <h3 className="mb-3 text-sm font-semibold text-gray-900 dark:text-gray-100">
              Recurrence
            </h3>
            <RecurrenceEditor
              value={recurrence}
              onChange={(newRecurrence) => setRecurrence(newRecurrence)}
            />
            {recurrence?.enabled && recurrence.rule && (
              <div className="mt-3 rounded-md border border-blue-200 bg-blue-50 p-2 dark:border-blue-800 dark:bg-blue-950">
                <RecurrencePreview rrule={recurrence.rule} count={3} />
              </div>
            )}
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
            <Button type="submit" disabled={isSubmitting || !title.trim()}>
              {isSubmitting
                ? isEditMode
                  ? 'Saving...'
                  : 'Creating...'
                : isEditMode
                  ? 'Save Changes'
                  : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
