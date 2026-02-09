'use client'

import * as React from 'react'
import * as ToastPrimitives from '@radix-ui/react-toast'
import { cva, type VariantProps } from 'class-variance-authority'

/**
 * Toast notification component built with Radix UI
 *
 * Used for in-app notifications including:
 * - Success messages
 * - Error messages
 * - Info messages
 * - Reminder notifications
 */

const ToastProvider = ToastPrimitives.Provider

const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={[
      'fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse gap-2 p-4',
      'sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[320px]',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    {...props}
  />
))
ToastViewport.displayName = ToastPrimitives.Viewport.displayName

const toastVariants = cva(
  [
    'group pointer-events-auto relative flex w-full items-center justify-between',
    'space-x-3 overflow-hidden rounded-md border p-3 pr-6 shadow-md',
    'transition-all',
    'data-[swipe=cancel]:translate-x-0',
    'data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)]',
    'data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)]',
    'data-[swipe=move]:transition-none',
    'data-[state=open]:animate-in data-[state=closed]:animate-out',
    'data-[swipe=end]:animate-out',
    'data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full',
    'data-[state=open]:slide-in-from-bottom-full data-[state=open]:sm:slide-in-from-bottom-full',
  ],
  {
    variants: {
      variant: {
        default: [
          'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800',
          'text-gray-900 dark:text-gray-100',
        ],
        success: [
          'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950',
          'text-green-900 dark:text-green-100',
        ],
        error: [
          'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950',
          'text-red-900 dark:text-red-100',
        ],
        warning: [
          'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950',
          'text-yellow-900 dark:text-yellow-100',
        ],
        info: [
          'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950',
          'text-blue-900 dark:text-blue-100',
        ],
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

const Toast = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Root> & VariantProps<typeof toastVariants>
>(({ className, variant, ...props }, ref) => {
  return (
    <ToastPrimitives.Root
      ref={ref}
      className={toastVariants({ variant, className })}
      {...props}
    />
  )
})
Toast.displayName = ToastPrimitives.Root.displayName

const ToastAction = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Action>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Action>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Action
    ref={ref}
    className={[
      'inline-flex h-8 shrink-0 items-center justify-center',
      'rounded-md border border-gray-200 dark:border-gray-700',
      'bg-transparent px-3 text-sm font-medium',
      'ring-offset-white transition-colors',
      'hover:bg-gray-100 dark:hover:bg-gray-800',
      'focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    {...props}
  />
))
ToastAction.displayName = ToastPrimitives.Action.displayName

const ToastClose = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Close>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Close>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={[
      'absolute right-2 top-2 rounded-md p-1',
      'text-gray-500 opacity-0 transition-opacity',
      'hover:text-gray-900 dark:hover:text-gray-100',
      'focus:opacity-100 focus:outline-none focus:ring-2',
      'group-hover:opacity-100',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    toast-close=""
    {...props}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  </ToastPrimitives.Close>
))
ToastClose.displayName = ToastPrimitives.Close.displayName

const ToastTitle = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Title>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Title>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Title
    ref={ref}
    className={['text-sm font-semibold', className].filter(Boolean).join(' ')}
    {...props}
  />
))
ToastTitle.displayName = ToastPrimitives.Title.displayName

const ToastDescription = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Description>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Description>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Description
    ref={ref}
    className={['text-sm opacity-90', className].filter(Boolean).join(' ')}
    {...props}
  />
))
ToastDescription.displayName = ToastPrimitives.Description.displayName

type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>

type ToastActionElement = React.ReactElement<typeof ToastAction>

export {
  type ToastProps,
  type ToastActionElement,
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
}
