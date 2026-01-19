import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

/**
 * Button component with multiple variants
 *
 * Built with class-variance-authority for type-safe variants
 * Supports different sizes, colors, and states
 */

const buttonVariants = cva(
  // Base styles
  [
    'inline-flex items-center justify-center',
    'rounded-lg font-medium',
    'transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
  ],
  {
    variants: {
      variant: {
        primary: [
          'bg-blue-600 text-white',
          'hover:bg-blue-700',
          'active:bg-blue-800',
          'focus-visible:ring-blue-600',
        ],
        secondary: [
          'bg-gray-200 text-gray-900',
          'hover:bg-gray-300',
          'active:bg-gray-400',
          'focus-visible:ring-gray-500',
          'dark:bg-gray-700 dark:text-gray-100',
          'dark:hover:bg-gray-600',
        ],
        outline: [
          'border-2 border-gray-300 bg-transparent text-gray-700',
          'hover:bg-gray-100',
          'active:bg-gray-200',
          'focus-visible:ring-gray-500',
          'dark:border-gray-600 dark:text-gray-200',
          'dark:hover:bg-gray-800',
        ],
        ghost: [
          'bg-transparent text-gray-700',
          'hover:bg-gray-100',
          'active:bg-gray-200',
          'focus-visible:ring-gray-500',
          'dark:text-gray-200',
          'dark:hover:bg-gray-800',
        ],
        danger: [
          'bg-red-600 text-white',
          'hover:bg-red-700',
          'active:bg-red-800',
          'focus-visible:ring-red-600',
        ],
        success: [
          'bg-green-600 text-white',
          'hover:bg-green-700',
          'active:bg-green-800',
          'focus-visible:ring-green-600',
        ],
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      fullWidth: false,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, fullWidth, loading, disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={buttonVariants({ variant, size, fullWidth, className })}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="mr-2 h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
