'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useCommandPaletteStore } from '@/lib/stores/useCommandPaletteStore'
import { useNewTaskModalStore } from '@/lib/stores/useNewTaskModalStore'
import { useTasks } from '@/lib/hooks/useTasks'
import { useNotes } from '@/lib/hooks/useNotes'
// Focus mode store is handled separately since it requires a task

interface CommandItem {
  id: string
  type: 'action' | 'task' | 'note' | 'page'
  title: string
  description?: string
  icon?: React.ReactNode
  onSelect: () => void
}

export function CommandPalette() {
  const router = useRouter()
  const { isOpen, close } = useCommandPaletteStore()
  const openNewTaskModal = useNewTaskModalStore((state) => state.open)
  const { data: tasks = [] } = useTasks({ hidden: false })
  const { data: notes = [] } = useNotes({ archived: false })

  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 0)
    }
  }, [isOpen])

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        useCommandPaletteStore.getState().toggle()
      }
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault()
        close()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, close])

  // Build command items
  const getCommands = useCallback((): CommandItem[] => {
    const actions: CommandItem[] = [
      {
        id: 'new-task',
        type: 'action',
        title: 'Create New Task',
        description: 'Add a new task to your list',
        icon: (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        ),
        onSelect: () => {
          close()
          openNewTaskModal()
        },
      },
      {
        id: 'go-focus',
        type: 'page',
        title: 'Go to Focus Mode',
        description: 'Navigate to focus mode page',
        icon: (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        ),
        onSelect: () => {
          close()
          router.push('/dashboard/focus')
        },
      },
      {
        id: 'go-dashboard',
        type: 'page',
        title: 'Go to Dashboard',
        description: 'Navigate to the main dashboard',
        icon: (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        ),
        onSelect: () => {
          close()
          router.push('/dashboard')
        },
      },
      {
        id: 'go-notes',
        type: 'page',
        title: 'Go to Notes',
        description: 'Navigate to notes page',
        icon: (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        ),
        onSelect: () => {
          close()
          router.push('/dashboard/notes')
        },
      },
    ]

    // Add tasks as searchable items
    const taskItems: CommandItem[] = tasks.slice(0, 5).map((task) => ({
      id: `task-${task.id}`,
      type: 'task' as const,
      title: task.title,
      description: task.completed ? 'Completed' : task.dueDate ? `Due: ${new Date(task.dueDate).toLocaleDateString()}` : undefined,
      icon: (
        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      ),
      onSelect: () => {
        close()
        router.push(`/dashboard/tasks/${task.id}`)
      },
    }))

    // Add notes as searchable items
    const noteItems: CommandItem[] = notes.slice(0, 5).map((note) => ({
      id: `note-${note.id}`,
      type: 'note' as const,
      title: note.content.slice(0, 50) + (note.content.length > 50 ? '...' : ''),
      description: new Date(note.updatedAt).toLocaleDateString(),
      icon: (
        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      ),
      onSelect: () => {
        close()
        router.push('/dashboard/notes')
      },
    }))

    return [...actions, ...taskItems, ...noteItems]
  }, [tasks, notes, close, router, openNewTaskModal])

  // Filter commands based on query
  const filteredCommands = getCommands().filter((cmd) => {
    if (!query) return true
    const searchQuery = query.toLowerCase()
    return (
      cmd.title.toLowerCase().includes(searchQuery) ||
      cmd.description?.toLowerCase().includes(searchQuery)
    )
  })

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) =>
          prev < filteredCommands.length - 1 ? prev + 1 : 0
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : filteredCommands.length - 1
        )
        break
      case 'Enter':
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].onSelect()
        }
        break
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={close}
      />

      {/* Dialog */}
      <div className="relative w-full max-w-lg rounded-lg border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-900">
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-gray-200 px-4 dark:border-gray-700">
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search tasks, notes, or type a command..."
            className="flex-1 border-0 bg-transparent py-4 text-gray-900 placeholder:text-gray-400 focus:outline-none dark:text-gray-100 dark:placeholder:text-gray-500"
          />
          <kbd className="hidden rounded bg-gray-100 px-2 py-1 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400 sm:inline">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <div className="py-6 text-center text-gray-500 dark:text-gray-400">
              No results found
            </div>
          ) : (
            <div className="space-y-1">
              {filteredCommands.map((cmd, index) => (
                <button
                  key={cmd.id}
                  onClick={() => cmd.onSelect()}
                  className={[
                    'flex w-full items-center gap-3 rounded-md px-3 py-2 text-left transition-colors',
                    index === selectedIndex
                      ? 'bg-blue-50 text-blue-900 dark:bg-blue-900/20 dark:text-blue-100'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800',
                  ].join(' ')}
                >
                  <span className="flex-shrink-0 text-gray-400 dark:text-gray-500">
                    {cmd.icon}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate font-medium">{cmd.title}</div>
                    {cmd.description && (
                      <div className="truncate text-sm text-gray-500 dark:text-gray-400">
                        {cmd.description}
                      </div>
                    )}
                  </div>
                  <span className="flex-shrink-0 rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                    {cmd.type}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-gray-200 px-4 py-2 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">↑↓</kbd>
            <span>Navigate</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">↵</kbd>
            <span>Select</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">⌘K</kbd>
            <span>Open</span>
          </div>
        </div>
      </div>
    </div>
  )
}
