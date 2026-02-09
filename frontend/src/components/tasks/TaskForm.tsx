'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Task, CreateTaskRequest, UpdateTaskRequest } from '@/lib/schemas/task.schema'
import { useCreateTask, useUpdateTask } from '@/lib/hooks/useTasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'

type Recurrence = {
  enabled: boolean
  rule: string
  timezone?: string
  instanceGenerationMode?: 'on_completion'
  humanReadable: string
}
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Textarea } from '@/components/ui/Textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { RecurrenceEditor } from '@/components/recurrence/RecurrenceEditor'
import { RecurrencePreview } from '@/components/recurrence/RecurrencePreview'

interface TaskFormProps {
  task?: Task
  onSuccess?: () => void
  onCancel?: () => void
}

export function TaskForm({ task, onSuccess, onCancel }: TaskFormProps) {
  const router = useRouter()
  const { toast } = useToast()
  const createTask = useCreateTask()
  const updateTask = useUpdateTask()

  const isEditing = !!task

  // Form state
  const [title, setTitle] = useState(task?.title || '')
  const [description, setDescription] = useState(task?.message || '')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>(task?.priority || 'medium')
  const [tags, setTags] = useState<string[]>((task as any)?.tags || [])
  const [tagInput, setTagInput] = useState('')
  const [dueDate, setDueDate] = useState(task?.due_date ? task.due_date.slice(0, 16) : '')
  const [estimatedDuration, setEstimatedDuration] = useState(task?.estimated_duration?.toString() || '')
  const [recurrence, setRecurrence] = useState<Recurrence | undefined>((task as any)?.recurrence)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      toast({
        title: 'Error',
        message: 'Task title is required',
        type: 'error',
      })
      return
    }

    setIsSubmitting(true)

    try {
      if (isEditing) {
        const updateData: UpdateTaskRequest = {
          title: title.trim(),
          message: description.trim(),
          priority,
          // tags, // TODO: Add tags to Task schema
          due_date: dueDate ? new Date(dueDate).toISOString() : null,
          estimated_duration: estimatedDuration ? parseInt(estimatedDuration, 10) : null,
          // recurrence, // TODO: Add recurrence to Task schema
        }
        await updateTask.mutateAsync({
          id: task.id,
          ...updateData,
        })

        toast({
          title: 'Task updated',
          message: 'Your task has been successfully updated',
          type: 'success',
        })
      } else {
        const createData: CreateTaskRequest = {
          title: title.trim(),
          message: description.trim(),
          priority,
          // tags, // TODO: Add tags to Task schema
          due_date: dueDate ? new Date(dueDate).toISOString() : null,
          estimated_duration: estimatedDuration ? parseInt(estimatedDuration, 10) : null,
          // recurrence, // TODO: Add recurrence to Task schema
        }
        const newTask = await createTask.mutateAsync(createData)

        toast({
          title: 'Task created',
          message: 'Your new task has been added',
          type: 'success',
        })

        router.push(`/dashboard/tasks/${newTask.data.id}`)
      }

      onSuccess?.()
    } catch (error) {
      toast({
        title: 'Error',
        message: isEditing ? 'Failed to update task' : 'Failed to create task',
        type: 'error',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAddTag = () => {
    const tag = tagInput.trim()
    if (tag && !tags.includes(tag) && tags.length < 20) {
      setTags([...tags, tag])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove))
  }

  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div>
        <Label htmlFor="title">
          Title <span className="text-red-500">*</span>
        </Label>
        <Input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          maxLength={200}
          required
          className="mt-1"
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {title.length}/200 characters
        </p>
      </div>

      {/* Description */}
      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details about this task..."
          rows={4}
          maxLength={1000}
          className="mt-1"
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {description.length}/1000 characters
        </p>
      </div>

      {/* Priority */}
      <div>
        <Label htmlFor="priority">Priority</Label>
        <Select
          value={priority}
          onValueChange={(value) => setPriority(value as 'low' | 'medium' | 'high')}
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

      {/* Tags */}
      <div>
        <Label htmlFor="tags">Tags</Label>
        <div className="mt-1 flex gap-2">
          <Input
            id="tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagInputKeyDown}
            placeholder="Add a tag..."
            maxLength={30}
            disabled={tags.length >= 20}
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddTag}
            disabled={!tagInput.trim() || tags.length >= 20}
          >
            Add
          </Button>
        </div>
        {tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-blue-600 dark:hover:text-blue-300"
                >
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {tags.length}/20 tags
        </p>
      </div>

      {/* Due Date */}
      <div>
        <Label htmlFor="dueDate">Due Date</Label>
        <Input
          id="dueDate"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="mt-1"
        />
      </div>

      {/* Estimated Duration */}
      <div>
        <Label htmlFor="estimatedDuration">Estimated Duration (minutes)</Label>
        <Input
          id="estimatedDuration"
          type="number"
          value={estimatedDuration}
          onChange={(e) => setEstimatedDuration(e.target.value)}
          placeholder="How long will this take?"
          min="1"
          max="720"
          className="mt-1"
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Max 720 minutes (12 hours)
        </p>
      </div>

      {/* Recurrence (T111) */}
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-900">
        <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-gray-100">
          Recurrence (FR-069)
        </h3>
        <RecurrenceEditor
          value={recurrence}
          onChange={(newRecurrence) => setRecurrence(newRecurrence)}
        />
        {recurrence?.enabled && recurrence.rule && (
          <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950">
            <RecurrencePreview rrule={recurrence.rule} count={5} />
          </div>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 border-t border-gray-200 pt-6 dark:border-gray-800">
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
          disabled={isSubmitting || !title.trim()}
          className="flex-1"
        >
          {isSubmitting
            ? isEditing
              ? 'Updating...'
              : 'Creating...'
            : isEditing
            ? 'Update Task'
            : 'Create Task'}
        </Button>
      </div>
    </form>
  )
}
