'use client'

import { useState } from 'react'
import { useCreateSubtask } from '@/lib/hooks/useSubtasks'
import { useToast } from '@/lib/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

/**
 * AddSubTaskForm component (T081)
 *
 * Provides a form to add new sub-tasks with:
 * - Max 10 sub-tasks limit enforcement (T081)
 * - Input validation
 * - Loading states
 */

interface AddSubTaskFormProps {
  taskId: string
  currentSubTaskCount: number
  onSuccess?: () => void
}

const MAX_SUBTASKS = 10 // T081: Maximum allowed sub-tasks

export function AddSubTaskForm({
  taskId,
  currentSubTaskCount,
  onSuccess,
}: AddSubTaskFormProps) {
  const [title, setTitle] = useState('')
  const createSubTask = useCreateSubtask()
  const { toast } = useToast()

  // T081: Check if max limit reached
  const isMaxReached = currentSubTaskCount >= MAX_SUBTASKS

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      toast({
        title: 'Error',
        message: 'Sub-task title is required',
        type: 'error',
      })
      return
    }

    // T081: Enforce max sub-tasks limit
    if (isMaxReached) {
      toast({
        title: 'Limit reached',
        message: `You can only add up to ${MAX_SUBTASKS} sub-tasks per task`,
        type: 'error',
      })
      return
    }

    try {
      await createSubTask.mutateAsync({
        taskId,
        title: title.trim(),
      })

      toast({
        title: 'Sub-task added',
        message: 'New sub-task has been created',
        type: 'success',
      })

      setTitle('') // Clear input
      onSuccess?.()
    } catch (error) {
      toast({
        title: 'Error',
        message: 'Failed to create sub-task',
        type: 'error',
      })
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <Input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isMaxReached
              ? `Maximum ${MAX_SUBTASKS} sub-tasks reached`
              : 'Add a sub-task...'
          }
          disabled={isMaxReached || createSubTask.isPending}
          maxLength={200}
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={!title.trim() || isMaxReached || createSubTask.isPending}
        >
          {createSubTask.isPending ? 'Adding...' : 'Add'}
        </Button>
      </div>

      {/* T081: Show limit warning when approaching max */}
      {currentSubTaskCount >= MAX_SUBTASKS - 2 && !isMaxReached && (
        <p className="text-xs text-yellow-600 dark:text-yellow-400">
          ⚠️ You have {MAX_SUBTASKS - currentSubTaskCount} sub-task
          {MAX_SUBTASKS - currentSubTaskCount === 1 ? '' : 's'} remaining
        </p>
      )}

      {/* T081: Show limit reached message */}
      {isMaxReached && (
        <p className="text-xs text-red-600 dark:text-red-400">
          Maximum limit of {MAX_SUBTASKS} sub-tasks reached. Delete some to add more.
        </p>
      )}

      <p className="text-xs text-gray-500 dark:text-gray-400">
        {currentSubTaskCount}/{MAX_SUBTASKS} sub-tasks
      </p>
    </form>
  )
}
