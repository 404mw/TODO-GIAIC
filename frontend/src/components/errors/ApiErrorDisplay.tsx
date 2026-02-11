/**
 * ApiErrorDisplay Component
 * Phase 5 - Error Handling
 *
 * Reusable component for displaying API errors with proper formatting.
 * Handles all error codes from API.md with user-friendly messages.
 *
 * Features:
 * - Color-coded severity levels (error/warning/info)
 * - Action buttons for specific error types (retry, upgrade, refetch)
 * - Auto-dismiss capability
 * - Request ID display for debugging
 * - Detailed error information in development mode
 */

'use client'

import { useState, useEffect } from 'react'
import { ApiError } from '@/lib/api/client'

interface ApiErrorDisplayProps {
  /** The error to display */
  error: ApiError | Error | string | null
  /** Callback when retry button is clicked */
  onRetry?: () => void
  /** Callback when upgrade button is clicked (for credit/tier errors) */
  onUpgrade?: () => void
  /** Callback when refetch button is clicked (for conflict errors) */
  onRefetch?: () => void
  /** Callback when dismiss button is clicked */
  onDismiss?: () => void
  /** Auto-dismiss after N milliseconds (0 = no auto-dismiss) */
  autoDismiss?: number
  /** Show detailed error information (development mode) */
  detailed?: boolean
  /** Custom CSS classes */
  className?: string
}

export function ApiErrorDisplay({
  error,
  onRetry,
  onUpgrade,
  onRefetch,
  onDismiss,
  autoDismiss = 0,
  detailed = false,
  className = '',
}: ApiErrorDisplayProps) {
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    if (autoDismiss > 0 && error) {
      const timer = setTimeout(() => {
        setDismissed(true)
        onDismiss?.()
      }, autoDismiss)
      return () => clearTimeout(timer)
    }
  }, [error, autoDismiss, onDismiss])

  useEffect(() => {
    // Reset dismissed state when error changes
    setDismissed(false)
  }, [error])

  if (!error || dismissed) {
    return null
  }

  const isApiError = error instanceof ApiError
  const errorCode = isApiError ? error.code : null
  const errorMessage = error instanceof Error ? error.message : String(error)
  const requestId = isApiError ? error.request_id : null
  const details = isApiError ? error.details : null

  // Determine severity and styling based on error code
  const { severity, icon, colors } = getErrorPresentation(errorCode)

  // Get user-friendly message and actions
  const { message, actions } = getErrorMessageAndActions(errorCode, errorMessage, {
    onRetry,
    onUpgrade,
    onRefetch,
  })

  const handleDismiss = () => {
    setDismissed(true)
    onDismiss?.()
  }

  return (
    <div className={`rounded-md ${colors.bg} ${colors.border} border p-4 ${className}`}>
      <div className="flex gap-3">
        {/* Icon */}
        <div className="shrink-0">
          <svg className={`h-5 w-5 ${colors.icon}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className={`text-sm font-medium ${colors.text}`}>{getSeverityLabel(severity)}</h3>
          <div className={`mt-1 text-sm ${colors.textSecondary}`}>
            <p>{message}</p>

            {/* Detailed error information (development mode) */}
            {detailed && (
              <div className="mt-2 space-y-1 text-xs opacity-75">
                {errorCode && <p>Error Code: {errorCode}</p>}
                {requestId && <p>Request ID: {requestId}</p>}
                {details !== null && details !== undefined && (
                  <p>Details: {JSON.stringify(details)}</p>
                )}
              </div>
            )}
          </div>

          {/* Action buttons */}
          {actions.length > 0 && (
            <div className="mt-3 flex gap-2">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.onClick}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium ${action.className} transition-colors`}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={handleDismiss}
            className={`shrink-0 ${colors.textSecondary} hover:${colors.text}`}
            aria-label="Dismiss error"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}

// Helper functions

function getSeverityLabel(severity: 'error' | 'warning' | 'info'): string {
  switch (severity) {
    case 'error':
      return 'Error'
    case 'warning':
      return 'Warning'
    case 'info':
      return 'Information'
  }
}

function getErrorPresentation(code: string | null): {
  severity: 'error' | 'warning' | 'info'
  icon: string
  colors: {
    bg: string
    border: string
    text: string
    textSecondary: string
    icon: string
  }
} {
  // Warning-level errors (user action required but not critical)
  const warningCodes = [
    'INSUFFICIENT_CREDITS',
    'TIER_REQUIRED',
    'RATE_LIMIT_EXCEEDED',
    'CONFLICT',
    'TASK_HAS_INCOMPLETE_SUBTASKS',
  ]

  // Info-level errors (informational, not failures)
  const infoCodes: string[] = []

  const severity = code && warningCodes.includes(code) ? 'warning' : code && infoCodes.includes(code) ? 'info' : 'error'

  const icons = {
    error:
      'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    warning:
      'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  }

  const colorSchemes = {
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      text: 'text-red-800 dark:text-red-200',
      textSecondary: 'text-red-700 dark:text-red-300',
      icon: 'text-red-600 dark:text-red-400',
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      text: 'text-yellow-800 dark:text-yellow-200',
      textSecondary: 'text-yellow-700 dark:text-yellow-300',
      icon: 'text-yellow-600 dark:text-yellow-400',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      text: 'text-blue-800 dark:text-blue-200',
      textSecondary: 'text-blue-700 dark:text-blue-300',
      icon: 'text-blue-600 dark:text-blue-400',
    },
  }

  return {
    severity,
    icon: icons[severity],
    colors: colorSchemes[severity],
  }
}

function getErrorMessageAndActions(
  code: string | null,
  fallbackMessage: string,
  callbacks: {
    onRetry?: () => void
    onUpgrade?: () => void
    onRefetch?: () => void
  }
): {
  message: string
  actions: Array<{ label: string; onClick: () => void; className: string }>
} {
  const actions: Array<{ label: string; onClick: () => void; className: string }> = []

  let message: string

  switch (code) {
    case 'VALIDATION_ERROR':
      message = 'Please check your input and try again.'
      break
    case 'UNAUTHORIZED':
      message = 'You are not authorized to perform this action. Please log in.'
      break
    case 'TOKEN_EXPIRED':
      message = 'Your session has expired. Please refresh the page to continue.'
      if (callbacks.onRetry) {
        actions.push({
          label: 'Refresh Page',
          onClick: () => window.location.reload(),
          className: 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300',
        })
      }
      break
    case 'INSUFFICIENT_CREDITS':
      message = 'You do not have enough credits for this action. Purchase more credits or upgrade to Pro.'
      if (callbacks.onUpgrade) {
        actions.push({
          label: 'Upgrade to Pro',
          onClick: callbacks.onUpgrade,
          className: 'bg-purple-600 text-white hover:bg-purple-700',
        })
      }
      break
    case 'TIER_REQUIRED':
      message = 'This feature requires a Pro subscription.'
      if (callbacks.onUpgrade) {
        actions.push({
          label: 'Upgrade Now',
          onClick: callbacks.onUpgrade,
          className: 'bg-purple-600 text-white hover:bg-purple-700',
        })
      }
      break
    case 'RATE_LIMIT_EXCEEDED':
      message = 'You have made too many requests. Please wait a moment and try again.'
      if (callbacks.onRetry) {
        actions.push({
          label: 'Try Again',
          onClick: callbacks.onRetry,
          className: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300',
        })
      }
      break
    case 'NOT_FOUND':
      message = 'The requested resource was not found.'
      break
    case 'TASK_NOT_FOUND':
      message = 'Task not found. It may have been deleted.'
      break
    case 'CONFLICT':
      message = 'This resource has been modified by another process. Please refresh and try again.'
      if (callbacks.onRefetch) {
        actions.push({
          label: 'Refresh',
          onClick: callbacks.onRefetch,
          className: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300',
        })
      }
      break
    case 'AI_SERVICE_UNAVAILABLE':
      message = 'AI service is temporarily unavailable. Please try again in a few moments.'
      if (callbacks.onRetry) {
        actions.push({
          label: 'Retry',
          onClick: callbacks.onRetry,
          className: 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300',
        })
      }
      break
    case 'TASK_HAS_INCOMPLETE_SUBTASKS':
      message = 'This task has incomplete subtasks. Complete or remove them before marking the task as complete.'
      break
    default:
      message = fallbackMessage || 'An unexpected error occurred. Please try again.'
      if (callbacks.onRetry) {
        actions.push({
          label: 'Retry',
          onClick: callbacks.onRetry,
          className: 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300',
        })
      }
  }

  return { message, actions }
}
