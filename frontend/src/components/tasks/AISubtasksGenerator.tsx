/**
 * AISubtasksGenerator Component
 * Phase 4 - Component Migration
 *
 * Provides UI for AI-powered sub-task generation using aiService.
 * Features:
 * - Real AI subtask generation via backend API
 * - Credit cost display and balance checking
 * - Loading state with animation
 * - Preview of generated sub-tasks before adding
 * - Comprehensive error handling (credits, tier, service availability)
 */

'use client'

import { useState, useEffect } from 'react'
import type { Subtask } from '@/lib/schemas/subtask.schema'
import { Button } from '@/components/ui/Button'
import { aiService } from '@/lib/services/ai.service'
import { ApiError } from '@/lib/api/client'

interface AISubtasksGeneratorProps {
  taskId: string
  taskTitle: string
  taskDescription?: string
  onSubtasksGenerated?: (subtasks: Omit<Subtask, 'id' | 'created_at' | 'updated_at'>[]) => void
}

export function AISubtasksGenerator({
  taskId,
  taskTitle,
  taskDescription,
  onSubtasksGenerated,
}: AISubtasksGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [previewSubtasks, setPreviewSubtasks] = useState<{ title: string }[]>([])
  const [showPreview, setShowPreview] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorType, setErrorType] = useState<'warning' | 'error' | 'info'>('error')
  const [creditsUsed, setCreditsUsed] = useState<number | null>(null)
  const [creditsRemaining, setCreditsRemaining] = useState<number | null>(null)

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  const handleGenerateClick = async () => {
    setIsGenerating(true)
    setError(null)
    setErrorType('error')

    try {
      // Call AI service to generate subtasks
      const response = await aiService.generateSubtasks(taskId)

      // Extract response data
      const { suggested_subtasks, credits_used, credits_remaining } = response.data

      // Check if we got any subtasks
      if (!suggested_subtasks || suggested_subtasks.length === 0) {
        setError('AI did not generate any subtasks. Try providing more details in the task description.')
        setErrorType('warning')
        return
      }

      // Update state with generated subtasks and credit info
      setPreviewSubtasks(suggested_subtasks)
      setCreditsUsed(credits_used)
      setCreditsRemaining(credits_remaining)
      setShowPreview(true)

      // Show success message
      setError(`Generated ${suggested_subtasks.length} subtasks (${credits_used} credit used, ${credits_remaining} remaining)`)
      setErrorType('info')
    } catch (err) {
      console.error('AI subtask generation error:', err)

      if (err instanceof ApiError) {
        switch (err.code) {
          case 'INSUFFICIENT_CREDITS':
            setError('Insufficient credits. Purchase more credits or upgrade to Pro for more daily credits.')
            setErrorType('warning')
            break
          case 'TIER_REQUIRED':
            setError('AI subtask generation requires a Pro subscription. Upgrade to unlock this feature.')
            setErrorType('warning')
            break
          case 'AI_SERVICE_UNAVAILABLE':
            setError('AI service is temporarily unavailable. Please try again in a few moments.')
            setErrorType('error')
            break
          case 'RATE_LIMIT_EXCEEDED':
            setError('Rate limit exceeded. Please wait a moment before trying again.')
            setErrorType('warning')
            break
          case 'TASK_NOT_FOUND':
            setError('Task not found. Please refresh and try again.')
            setErrorType('error')
            break
          default:
            setError(`Failed to generate subtasks: ${err.message}`)
            setErrorType('error')
        }
      } else {
        setError('Failed to generate subtasks. Please try again.')
        setErrorType('error')
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleAddSubtasks = () => {
    if (onSubtasksGenerated && previewSubtasks.length > 0) {
      const now = new Date().toISOString()
      const subtasks = previewSubtasks.map((subtask, index) => ({
        title: subtask.title,
        completed: false,
        completed_at: null,
        task_id: taskId,
        order_index: index,
        source: 'ai' as const,
        created_at: now,
        updated_at: now,
      }))
      onSubtasksGenerated(subtasks)
    }
    setShowPreview(false)
    setPreviewSubtasks([])
  }

  const handleRemovePreview = (index: number) => {
    setPreviewSubtasks((prev) => prev.filter((_, i) => i !== index))
  }

  const handleCancelPreview = () => {
    setShowPreview(false)
    setPreviewSubtasks([])
  }

  const getErrorColors = () => {
    switch (errorType) {
      case 'warning':
        return {
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-yellow-200 dark:border-yellow-800',
          text: 'text-yellow-700 dark:text-yellow-300',
          icon: 'text-yellow-600 dark:text-yellow-400',
        }
      case 'info':
        return {
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-blue-200 dark:border-blue-800',
          text: 'text-blue-700 dark:text-blue-300',
          icon: 'text-blue-600 dark:text-blue-400',
        }
      default:
        return {
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-red-200 dark:border-red-800',
          text: 'text-red-700 dark:text-red-300',
          icon: 'text-red-600 dark:text-red-400',
        }
    }
  }

  const errorColors = getErrorColors()

  return (
    <div className="space-y-4">
      {/* Generate Button */}
      {!showPreview && (
        <div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleGenerateClick}
            disabled={isGenerating}
            className="gap-2"
          >
            {isGenerating ? (
              <>
                <svg
                  className="h-4 w-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                AI Generate Subtasks
                <span className="ml-1 rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                  1 credit
                </span>
              </>
            )}
          </Button>

          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            AI will analyze your task and suggest actionable subtasks to help you break it down.
          </p>
        </div>
      )}

      {/* Error/Info Message */}
      {error && (
        <div className={`rounded-md ${errorColors.bg} ${errorColors.border} border p-3`}>
          <div className="flex gap-2">
            <svg
              className={`h-5 w-5 flex-shrink-0 ${errorColors.icon}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {errorType === 'info' ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              )}
            </svg>
            <p className={`text-sm ${errorColors.text}`}>{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className={`mt-2 text-xs ${errorColors.text} underline hover:no-underline`}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Preview of Generated Subtasks */}
      {showPreview && previewSubtasks.length > 0 && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
          <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-blue-900 dark:text-blue-100">
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            AI-Generated Subtasks Preview
            {creditsUsed && (
              <span className="ml-auto rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                {creditsUsed} credit used
              </span>
            )}
          </h4>

          <ul className="space-y-2">
            {previewSubtasks.map((subtask, index) => (
              <li
                key={index}
                className="flex items-center justify-between gap-2 rounded-md bg-white p-2 text-sm dark:bg-gray-800"
              >
                <span className="text-gray-700 dark:text-gray-300">{subtask.title}</span>
                <button
                  onClick={() => handleRemovePreview(index)}
                  className="text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                  aria-label={`Remove "${subtask.title}"`}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>

          {creditsRemaining !== null && (
            <p className="mt-3 text-xs text-blue-600 dark:text-blue-400">
              {creditsRemaining} credits remaining
            </p>
          )}

          <div className="mt-4 flex gap-2">
            <Button size="sm" onClick={handleAddSubtasks}>
              Add {previewSubtasks.length} Subtask{previewSubtasks.length !== 1 ? 's' : ''}
            </Button>
            <Button variant="outline" size="sm" onClick={handleCancelPreview}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
