/**
 * Skeleton Component (T188)
 * Phase 15 - Polish
 *
 * Animated loading placeholder for async content.
 * Uses shimmer animation for visual feedback.
 */

import { cn } from '@/lib/utils/cn'

interface SkeletonProps {
  className?: string
}

/**
 * Base skeleton component with pulse animation
 */
export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-white/10',
        className
      )}
    />
  )
}

/**
 * Task card skeleton for loading states
 */
export function TaskCardSkeleton() {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-start gap-3">
        {/* Checkbox placeholder */}
        <Skeleton className="h-5 w-5 rounded" />

        <div className="flex-1 space-y-3">
          {/* Title */}
          <Skeleton className="h-5 w-3/4" />

          {/* Description */}
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />

          {/* Tags and metadata */}
          <div className="flex gap-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2">
          <Skeleton className="h-8 w-8 rounded-lg" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
      </div>
    </div>
  )
}

/**
 * Task list skeleton (multiple cards)
 */
export function TaskListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <TaskCardSkeleton key={i} />
      ))}
    </div>
  )
}

/**
 * Note card skeleton for loading states
 */
export function NoteCardSkeleton() {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="space-y-3">
        {/* Content lines */}
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-3/5" />

        {/* Metadata */}
        <div className="flex items-center justify-between pt-2">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-6 w-6 rounded" />
        </div>
      </div>
    </div>
  )
}

/**
 * Note list skeleton (grid of cards)
 */
export function NoteListSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <NoteCardSkeleton key={i} />
      ))}
    </div>
  )
}

/**
 * Metric card skeleton for achievement/stats loading
 */
export function MetricCardSkeleton() {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <div className="space-y-4">
        {/* Icon placeholder */}
        <Skeleton className="h-12 w-12 rounded-xl" />

        {/* Title */}
        <Skeleton className="h-4 w-24" />

        {/* Value */}
        <Skeleton className="h-8 w-16" />

        {/* Subtitle */}
        <Skeleton className="h-3 w-32" />
      </div>
    </div>
  )
}

/**
 * Metric grid skeleton
 */
export function MetricGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <MetricCardSkeleton key={i} />
      ))}
    </div>
  )
}

/**
 * Sidebar navigation skeleton
 */
export function SidebarSkeleton() {
  return (
    <div className="space-y-4 p-4">
      {/* Logo */}
      <div className="flex items-center gap-2 px-2">
        <Skeleton className="h-8 w-8 rounded-lg" />
        <Skeleton className="h-5 w-24" />
      </div>

      {/* Search */}
      <Skeleton className="h-10 w-full rounded-lg" />

      {/* Nav items */}
      <div className="space-y-2 pt-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full rounded-lg" />
        ))}
      </div>

      {/* User profile */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Form field skeleton
 */
export function FormFieldSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-10 w-full rounded-lg" />
    </div>
  )
}

/**
 * Full page loading skeleton
 */
export function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-10 w-32 rounded-lg" />
      </div>

      {/* Content */}
      <TaskListSkeleton count={3} />
    </div>
  )
}
