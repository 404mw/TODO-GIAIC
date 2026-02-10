import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

/**
 * Input component with error states and variants
 *
 * Supports:
 * - Different sizes
 * - Error states with validation messages
 * - Optional labels
 * - Icon support (left/right)
 */

const inputVariants = cva(
  [
    'w-full rounded-lg border',
    'bg-white dark:bg-gray-900',
    'text-gray-900 dark:text-gray-100',
    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
    'transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
    // Fix calendar/date picker icon visibility in dark mode
    'dark:[color-scheme:dark]',
  ],
  {
    variants: {
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-5 text-lg',
      },
      state: {
        default: [
          'border-gray-300 dark:border-gray-600',
          'focus:border-blue-500 focus:ring-blue-600',
        ],
        error: [
          'border-red-500 dark:border-red-400',
          'focus:border-red-500 focus:ring-red-600',
        ],
        success: [
          'border-green-500 dark:border-green-400',
          'focus:border-green-500 focus:ring-green-600',
        ],
      },
    },
    defaultVariants: {
      size: 'md',
      state: 'default',
    },
  }
)

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      size,
      state,
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${React.useId()}`
    const errorId = error ? `${inputId}-error` : undefined
    const helperTextId = helperText ? `${inputId}-helper` : undefined

    const computedState = error ? 'error' : state

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {label}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={errorId || helperTextId}
            className={inputVariants({
              size,
              state: computedState,
              className: [
                className,
                leftIcon && 'pl-10',
                rightIcon && 'pr-10',
              ].filter(Boolean).join(' '),
            })}
            {...props}
          />

          {rightIcon && (
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>

        {error && (
          <p id={errorId} className="mt-1.5 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={helperTextId} className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
