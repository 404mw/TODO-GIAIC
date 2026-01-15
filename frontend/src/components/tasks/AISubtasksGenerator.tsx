/**
 * AISubtasksGenerator Component (T148-T150)
 * Phase 12 - AI Sub-tasks UI
 *
 * Provides UI for AI-powered sub-task generation.
 * Currently disabled until backend AI integration is complete.
 *
 * Features:
 * - Button to trigger AI sub-task generation (disabled state)
 * - Loading state with animation
 * - Preview of generated sub-tasks before adding
 * - Error handling for AI failures
 */

'use client'

import { useState } from 'react'
import type { SubTask } from '@/lib/schemas/subtask.schema'
import { Button } from '@/components/ui/Button'

interface AISubtasksGeneratorProps {
  taskId: string
  taskTitle: string
  taskDescription?: string
  onSubtasksGenerated?: (subtasks: Omit<SubTask, 'id' | 'createdAt' | 'updatedAt'>[]) => void
}

// Mock AI-generated subtasks for demo purposes
const MOCK_SUBTASKS = [
  'Break down the main objective',
  'Research required resources',
  'Set up the environment',
  'Implement core functionality',
  'Test and validate',
  'Document the process',
]

export function AISubtasksGenerator({
  taskId,
  taskTitle,
  taskDescription,
  onSubtasksGenerated,
}: AISubtasksGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [previewSubtasks, setPreviewSubtasks] = useState<string[]>([])
  const [showPreview, setShowPreview] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // AI is currently disabled - will be enabled with backend integration
  const aiEnabled = false

  const handleGenerateClick = async () => {
    if (!aiEnabled) {
      // Show disabled message
      setError('AI sub-task generation is coming soon! This feature is currently under development.')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      // This would call the AI API when enabled
      // const response = await fetch('/api/ai/generate-subtasks', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ taskId, taskTitle, taskDescription }),
      // })
      // const { subtasks } = await response.json()

      // For now, use mock data after a delay
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Filter mock subtasks based on task title length as a simple demo
      const count = Math.min(Math.max(3, Math.floor(taskTitle.length / 10)), 6)
      const generated = MOCK_SUBTASKS.slice(0, count)

      setPreviewSubtasks(generated)
      setShowPreview(true)
    } catch (err) {
      setError('Failed to generate sub-tasks. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleAddSubtasks = () => {
    if (onSubtasksGenerated) {
      const subtasks = previewSubtasks.map((title) => ({
        title,
        completed: false,
        completedAt: null,
        parentTaskId: taskId,
        estimatedDuration: null,
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
                AI Generate Sub-tasks
                {!aiEnabled && (
                  <span className="ml-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
                    Coming Soon
                  </span>
                )}
              </>
            )}
          </Button>

          {/* Disabled message */}
          {!aiEnabled && (
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              AI-powered sub-task generation will automatically break down complex tasks into manageable steps.
            </p>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-yellow-50 p-3 dark:bg-yellow-900/20">
          <div className="flex gap-2">
            <svg
              className="h-5 w-5 flex-shrink-0 text-yellow-600 dark:text-yellow-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="text-sm text-yellow-700 dark:text-yellow-300">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs text-yellow-600 underline hover:no-underline dark:text-yellow-400"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Preview of Generated Sub-tasks */}
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
            AI-Generated Sub-tasks Preview
          </h4>

          <ul className="space-y-2">
            {previewSubtasks.map((subtask, index) => (
              <li
                key={index}
                className="flex items-center justify-between gap-2 rounded-md bg-white p-2 text-sm dark:bg-gray-800"
              >
                <span className="text-gray-700 dark:text-gray-300">{subtask}</span>
                <button
                  onClick={() => handleRemovePreview(index)}
                  className="text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                  aria-label={`Remove "${subtask}"`}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>

          <div className="mt-4 flex gap-2">
            <Button size="sm" onClick={handleAddSubtasks}>
              Add {previewSubtasks.length} Sub-tasks
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
