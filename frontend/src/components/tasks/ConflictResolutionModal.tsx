'use client'

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/Dialog'
import { Button } from '@/components/ui/Button'
import type { Task } from '@/lib/schemas/task.schema'

interface ConflictResolutionModalProps {
  isOpen: boolean
  localVersion: Task
  serverVersion: Task
  onKeepMine: () => void
  onTakeTheirs: () => void
  onCancel: () => void
}

/**
 * T112 — ConflictResolutionModal
 *
 * Shown when useUpdateTask fails with VERSION_CONFLICT (HTTP 409).
 * Displays a side-by-side diff of the local version vs server version,
 * and lets the user resolve the conflict by keeping their changes,
 * accepting the server's changes, or cancelling.
 */
export function ConflictResolutionModal({
  isOpen,
  localVersion,
  serverVersion,
  onKeepMine,
  onTakeTheirs,
  onCancel,
}: ConflictResolutionModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onCancel()}>
      <DialogContent className="sm:max-w-[700px] w-[calc(100vw-2rem)]" hideCloseButton>
        <DialogHeader>
          <DialogTitle>Version Conflict</DialogTitle>
          <DialogDescription>
            Someone else (or another device) updated this task while you were editing it. Choose
            which version to keep.
          </DialogDescription>
        </DialogHeader>

        {/* Side-by-side diff */}
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {/* Your version */}
          <div className="rounded-lg border-2 border-blue-400 bg-blue-50 p-4 dark:border-blue-600 dark:bg-blue-950/30">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-300">
              Your version
            </h3>
            <VersionDisplay task={localVersion} />
          </div>

          {/* Server version */}
          <div className="rounded-lg border-2 border-orange-400 bg-orange-50 p-4 dark:border-orange-600 dark:bg-orange-950/30">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-orange-700 dark:text-orange-300">
              Server version
            </h3>
            <VersionDisplay task={serverVersion} />
          </div>
        </div>

        <DialogFooter className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="secondary" size="sm" onClick={onTakeTheirs}>
            Take theirs
          </Button>
          <Button variant="primary" size="sm" onClick={onKeepMine}>
            Keep mine
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function VersionDisplay({ task }: { task: Task }) {
  return (
    <div className="space-y-2 text-sm text-gray-800 dark:text-gray-200">
      <div>
        <span className="font-medium text-gray-500 dark:text-gray-400">Title: </span>
        {task.title}
      </div>
      {task.description && (
        <div>
          <span className="font-medium text-gray-500 dark:text-gray-400">Description: </span>
          <span className="line-clamp-3">{task.description}</span>
        </div>
      )}
      <div>
        <span className="font-medium text-gray-500 dark:text-gray-400">Priority: </span>
        {task.priority}
      </div>
      {task.due_date && (
        <div>
          <span className="font-medium text-gray-500 dark:text-gray-400">Due: </span>
          {new Date(task.due_date).toLocaleDateString()}
        </div>
      )}
      <div>
        <span className="font-medium text-gray-500 dark:text-gray-400">Version: </span>
        {task.version}
      </div>
    </div>
  )
}
