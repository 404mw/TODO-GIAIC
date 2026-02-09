'use client'

import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { PendingCompletionsBar } from './PendingCompletionsBar'
import { useSidebarStore } from '@/lib/stores/useSidebarStore'
import { useNewTaskModalStore } from '@/lib/stores/new-task-modal.store'
import { usePendingCompletionsStore } from '@/lib/stores/usePendingCompletionsStore'
import { NewTaskModal } from '@/components/tasks/NewTaskModal'

/**
 * Dashboard layout wrapper
 *
 * Provides the main application layout with:
 * - Collapsible sidebar
 * - Fixed header
 * - Responsive main content area
 * - Glassmorphism effects
 */

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { isOpen } = useSidebarStore()
  const { isOpen: isNewTaskModalOpen, editTask, close: closeNewTaskModal } =
    useNewTaskModalStore()
  const pendingCount = usePendingCompletionsStore((state) => state.getPendingCount())

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar />

      <div
        className={[
          'transition-all duration-300 ease-in-out',
          isOpen ? 'lg:ml-64' : 'lg:ml-[72px]',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <Header />

        <main
          className={[
            'min-h-[calc(100vh-4rem)] p-4 lg:p-6',
            pendingCount > 0 ? 'pb-20' : '', // Add padding when bottom bar is visible
          ]
            .filter(Boolean)
            .join(' ')}
        >
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>

      {/* Pending Completions Bottom Bar */}
      <PendingCompletionsBar />

      {/* New Task Modal */}
      <NewTaskModal
        open={isNewTaskModalOpen}
        onOpenChange={(open) => !open && closeNewTaskModal()}
        editTask={editTask}
      />
    </div>
  )
}
