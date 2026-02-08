'use client'

import { useState } from 'react'
import type { Task, TaskDetail } from '@/lib/schemas/task.schema'
import type { ReminderCreate } from '@/lib/schemas/reminder.schema'
import { REMINDER_PRESETS, REMINDER_PRESET_LABELS } from '@/lib/schemas/reminder.schema'
import { Button } from '@/components/ui/Button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select'

interface ReminderFormProps {
  task: Task | TaskDetail
  onSubmit: (reminder: ReminderCreate) => void | Promise<void>
  onCancel?: () => void
}

/**
 * ReminderForm component for creating task reminders
 * Per research.md Section 15 and tasks.md T088
 *
 * Features:
 * - Validates task has due date (FR-071)
 * - Relative timing offset selector (-15, -30, -60, -1440 minutes)
 * - Shows error if no due date present
 */
export function ReminderForm({ task, onSubmit, onCancel }: ReminderFormProps) {
  const [offsetMinutes, setOffsetMinutes] = useState<number>(REMINDER_PRESETS.FIFTEEN_MINUTES)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Validation: Task must have due date for reminders
  const hasDueDate = task.dueDate !== null && task.dueDate !== undefined

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate offset is a valid number
    if (isNaN(offsetMinutes)) {
      setError('Invalid offset value')
      return
    }

    // Double-check due date (shouldn't happen if form is properly disabled)
    if (!hasDueDate) {
      setError('Task must have a due date to set reminders')
      return
    }

    try {
      setIsSubmitting(true)

      const reminderData: ReminderCreate = {
        type: 'before',
        offsetMinutes,
        scheduledAt: null,
        method: 'in_app',
      }

      await onSubmit(reminderData)

      // Reset form on success
      setOffsetMinutes(REMINDER_PRESETS.FIFTEEN_MINUTES)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create reminder')
    } finally {
      setIsSubmitting(false)
    }
  }

  // If task has no due date, show error message instead of form
  if (!hasDueDate) {
    return (
      <div
        className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-4 text-amber-200"
        role="alert"
      >
        <p className="font-medium">Task must have a due date to set reminders</p>
        <p className="mt-1 text-sm text-amber-300/80">
          Please add a due date to this task before creating reminders.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="reminder-time"
          className="block text-sm font-medium text-gray-200 mb-2"
        >
          Reminder Time
        </label>
        <Select
          value={offsetMinutes.toString()}
          onValueChange={(value) => setOffsetMinutes(parseInt(value, 10))}
          disabled={isSubmitting}
        >
          <SelectTrigger id="reminder-time" className="w-full">
            <SelectValue placeholder="Select reminder time" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={REMINDER_PRESETS.FIFTEEN_MINUTES.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.FIFTEEN_MINUTES]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.THIRTY_MINUTES.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.THIRTY_MINUTES]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.ONE_HOUR.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.ONE_HOUR]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.ONE_DAY.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.ONE_DAY]}
            </SelectItem>
          </SelectContent>
        </Select>
        <p className="mt-1 text-sm text-gray-400">
          You'll be notified via browser notification and in-app toast
        </p>
      </div>

      {error && (
        <div
          className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-red-200"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="flex gap-3 justify-end">
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        )}
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
          aria-label="Add reminder"
        >
          {isSubmitting ? 'Adding...' : 'Add Reminder'}
        </Button>
      </div>
    </form>
  )
}
