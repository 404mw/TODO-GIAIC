'use client'

import * as React from 'react'

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {}

export const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={[
          'text-sm font-medium text-gray-700 dark:text-gray-300',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
        {...props}
      />
    )
  }
)

Label.displayName = 'Label'
