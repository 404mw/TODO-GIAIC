'use client'

import { useState } from 'react'
import type { Task } from '@/lib/schemas/task.schema'
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
  task: Task
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
  const [offsetMinutes, setOffsetMinutes] = useState<number>(REMINDER_PRESETS.FIFTEEN_MIN_BEFORE)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Validation: Task must have due date for reminders
  const hasDueDate = task.due_date !== null && task.due_date !== undefined

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

      // Calculate scheduled_at time based on due_date and offset
      const dueDate = new Date(task.due_date!)
      const scheduledAt = new Date(dueDate.getTime() + offsetMinutes * 60 * 1000)

      const reminderData: ReminderCreate = {
        type: offsetMinutes < 0 ? 'before' : offsetMinutes > 0 ? 'after' : 'absolute',
        offset_minutes: offsetMinutes,
        scheduled_at: scheduledAt.toISOString(),
        method: 'in_app',
      }

      await onSubmit(reminderData)

      // Reset form on success
      setOffsetMinutes(REMINDER_PRESETS.FIFTEEN_MIN_BEFORE)
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
            <SelectItem value={REMINDER_PRESETS.FIFTEEN_MIN_BEFORE.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.FIFTEEN_MIN_BEFORE]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.THIRTY_MIN_BEFORE.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.THIRTY_MIN_BEFORE]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.ONE_HOUR_BEFORE.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.ONE_HOUR_BEFORE]}
            </SelectItem>
            <SelectItem value={REMINDER_PRESETS.ONE_DAY_BEFORE.toString()}>
              {REMINDER_PRESET_LABELS[REMINDER_PRESETS.ONE_DAY_BEFORE]}
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
