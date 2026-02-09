'use client'

import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TaskList } from '@/components/tasks/TaskList'
import { useTasks } from '@/lib/hooks/useTasks'
import { useAchievements } from '@/lib/hooks/useAchievements'

/**
 * Dashboard home page
 *
 * Displays:
 * - Welcome message with current streak
 * - High-priority tasks
 * - Today's tasks (due today)
 * - Quick stats
 */

export default function DashboardPage() {
  // Fetch data
  const {
    data: tasksResponse,
    isLoading: tasksLoading,
    error: tasksError,
  } = useTasks({ completed: false })
  const { data: achievementsResponse, isLoading: achievementsLoading } = useAchievements()

  // Unwrap API responses
  const tasks = tasksResponse?.data || []
  const achievements = achievementsResponse?.data

  // Filter high-priority incomplete tasks
  const highPriorityTasks = tasks
    .filter((t) => t.priority === 'high' && !t.completed)
    .slice(0, 5)

  // Filter tasks due today
  const today = new Date().toISOString().split('T')[0]
  const todayTasks = tasks
    .filter((t) => t.due_date && t.due_date.startsWith(today) && !t.completed)
    .slice(0, 5)

  // Calculate stats
  const completedToday = tasks.filter(
    (t) => t.completed_at && t.completed_at.split('T')[0] === today
  ).length
  const totalActive = tasks.filter((t) => !t.completed).length
  const currentStreak = 0 // TODO: Fix when achievements structure is defined

  // Filter overdue tasks (due date before today and not completed)
  const overdueTasks = tasks.filter(
    (t) => t.due_date && t.due_date.split('T')[0] < today && !t.completed
  )

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Dashboard
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Welcome back! Here&apos;s your productivity overview.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {/* Current Streak */}
          <div className="group relative rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-orange-500/20 dark:hover:shadow-orange-500/10">
            <div className="absolute inset-0 rounded-lg bg-linear-to-br from-orange-500/0 to-orange-500/0 group-hover:from-orange-500/5 group-hover:to-orange-500/10 dark:group-hover:from-orange-500/10 dark:group-hover:to-orange-500/5 transition-all duration-300" />
            <div className="relative flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-950">
                <svg
                  className="h-6 w-6 text-orange-600 dark:text-orange-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Current Streak</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {achievementsLoading ? '...' : `${currentStreak} days`}
                </p>
              </div>
            </div>
          </div>

          {/* Completed Today */}
          <div className="group relative rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-green-500/20 dark:hover:shadow-green-500/10">
            <div className="absolute inset-0 rounded-lg bg-linear-to-br from-green-500/0 to-green-500/0 group-hover:from-green-500/5 group-hover:to-green-500/10 dark:group-hover:from-green-500/10 dark:group-hover:to-green-500/5 transition-all duration-300" />
            <div className="relative flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 dark:bg-green-950">
                <svg
                  className="h-6 w-6 text-green-600 dark:text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed Today</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {completedToday}
                </p>
              </div>
            </div>
          </div>

          {/* Active Tasks */}
          <div className="group relative rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-500/20 dark:hover:shadow-blue-500/10">
            <div className="absolute inset-0 rounded-lg bg-linear-to-br from-blue-500/0 to-blue-500/0 group-hover:from-blue-500/5 group-hover:to-blue-500/10 dark:group-hover:from-blue-500/10 dark:group-hover:to-blue-500/5 transition-all duration-300" />
            <div className="relative flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-950">
                <svg
                  className="h-6 w-6 text-blue-600 dark:text-blue-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active Tasks</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {totalActive}
                </p>
              </div>
            </div>
          </div>

          {/* Overdue Tasks */}
          <div className="group relative rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-red-500/20 dark:hover:shadow-red-500/10">
            <div className="absolute inset-0 rounded-lg bg-linear-to-br from-red-500/0 to-red-500/0 group-hover:from-red-500/5 group-hover:to-red-500/10 dark:group-hover:from-red-500/10 dark:group-hover:to-red-500/5 transition-all duration-300" />
            <div className="relative flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100 dark:bg-red-950">
                <svg
                  className="h-6 w-6 text-red-600 dark:text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Overdue</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {tasksLoading ? '...' : overdueTasks.length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* High Priority Tasks */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              High Priority
            </h2>
            {highPriorityTasks.length > 0 && (
              <span className="text-sm text-gray-500">{highPriorityTasks.length} tasks</span>
            )}
          </div>
          <TaskList
            tasks={highPriorityTasks}
            isLoading={tasksLoading}
            error={tasksError}
            emptyMessage="No high-priority tasks - you're all caught up!"
          />
        </div>

        {/* Today's Tasks */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Due Today
            </h2>
            {todayTasks.length > 0 && (
              <span className="text-sm text-gray-500">{todayTasks.length} tasks</span>
            )}
          </div>
          <TaskList
            tasks={todayTasks}
            isLoading={tasksLoading}
            error={tasksError}
            emptyMessage="No tasks due today - enjoy your free time!"
          />
        </div>
      </div>
    </DashboardLayout>
  )
}
