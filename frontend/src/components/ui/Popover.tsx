'use client'

import * as PopoverPrimitive from '@radix-ui/react-popover'
import * as React from 'react'

/**
 * Popover Component
 *
 * Based on Radix UI Popover primitive.
 * Provides accessible popover menus with proper focus management and portal rendering.
 *
 * Usage:
 * <Popover>
 *   <PopoverTrigger>Click me</PopoverTrigger>
 *   <PopoverContent>
 *     <p>Content here</p>
 *   </PopoverContent>
 * </Popover>
 */

const Popover = PopoverPrimitive.Root
const PopoverTrigger = PopoverPrimitive.Trigger
const PopoverAnchor = PopoverPrimitive.Anchor

interface PopoverContentProps
  extends React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content> {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

const PopoverContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  PopoverContentProps
>(({ className = '', align = 'center', sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      className={[
        'z-50 w-72 rounded-lg border border-gray-200 dark:border-gray-800',
        'bg-white dark:bg-gray-900 p-4 shadow-lg',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
        'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        'data-[side=bottom]:slide-in-from-top-2',
        'data-[side=left]:slide-in-from-right-2',
        'data-[side=right]:slide-in-from-left-2',
        'data-[side=top]:slide-in-from-bottom-2',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    />
  </PopoverPrimitive.Portal>
))
PopoverContent.displayName = PopoverPrimitive.Content.displayName

export { Popover, PopoverTrigger, PopoverContent, PopoverAnchor }
