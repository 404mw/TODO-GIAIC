'use client'

import * as React from 'react'
import * as SelectPrimitive from '@radix-ui/react-select'

/**
 * Select component built with Radix UI
 *
 * Accessible dropdown select with keyboard navigation
 * and proper ARIA attributes
 */

const Select = SelectPrimitive.Root
const SelectGroup = SelectPrimitive.Group
const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={[
      'flex h-10 w-full items-center justify-between',
      'rounded-lg border border-gray-300 dark:border-gray-600',
      'bg-white dark:bg-gray-900',
      'px-4 py-2 text-base',
      'text-gray-900 dark:text-gray-100',
      'placeholder:text-gray-400 dark:placeholder:text-gray-500',
      'focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'transition-colors duration-200',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
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
        className="opacity-50"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = 'popper', ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={[
        'relative z-50 min-w-[8rem] overflow-hidden',
        'rounded-lg border border-gray-200 dark:border-gray-700',
        'bg-white dark:bg-gray-800',
        'text-gray-900 dark:text-gray-100',
        'shadow-lg',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
        'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        position === 'popper' && 'data-[side=bottom]:translate-y-1 data-[side=top]:-translate-y-1',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      position={position}
      {...props}
    >
      <SelectPrimitive.Viewport
        className={[
          'p-1',
          position === 'popper' &&
            'h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {children}
      </SelectPrimitive.Viewport>
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectLabel = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Label>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={[
      'px-2 py-1.5 text-sm font-semibold',
      'text-gray-900 dark:text-gray-100',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    {...props}
  />
))
SelectLabel.displayName = SelectPrimitive.Label.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={[
      'relative flex w-full cursor-pointer select-none items-center',
      'rounded-md py-2 pl-8 pr-2',
      'text-base outline-none',
      'focus:bg-gray-100 dark:focus:bg-gray-700',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      'transition-colors duration-150',
      className,
    ]
      .filter(Boolean)
      .join(' ')}
    {...props}
  >
    <span className="absolute left-2 flex h-4 w-4 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
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
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </SelectPrimitive.ItemIndicator>
    </span>

    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

const SelectSeparator = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={['-mx-1 my-1 h-px bg-gray-200 dark:bg-gray-700', className]
      .filter(Boolean)
      .join(' ')}
    {...props}
  />
))
SelectSeparator.displayName = SelectPrimitive.Separator.displayName

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
}
