import { http, HttpResponse, delay } from 'msw'
import type { AchievementResponse } from '@/lib/schemas/achievement.schema'
import { achievementFixture } from '../data/user.fixture'

// In-memory storage (using fixture data)
let achievement: AchievementResponse = { ...achievementFixture }

// Track last completion date for streak calculation
let lastCompletionDate: string | null = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
  .toISOString()
  .split('T')[0]

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Helper: Calculate streak from task completions
const calculateStreak = (lastDate: string | null): number => {
  if (!lastDate) {
    return 0
  }

  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0]

  // If completed today or yesterday, maintain streak
  if (lastDate === today || lastDate === yesterday) {
    return achievement.stats.currentStreak
  }

  // Streak is broken
  return 0
}

// Helper: Check and unlock achievements
const checkUnlocks = (achievement: AchievementResponse): AchievementResponse => {
  const newUnlocked = [...achievement.unlocked]
  const newProgress = [...achievement.progress]

  // Check streak achievements
  const streakThresholds = [
    { id: 'streak_7', name: 'Week Warrior', threshold: 7, perkType: 'max_tasks' as const, perkValue: 10 },
    { id: 'streak_14', name: 'Fortnight Champion', threshold: 14, perkType: 'max_tasks' as const, perkValue: 20 },
    { id: 'streak_30', name: 'Monthly Master', threshold: 30, perkType: 'daily_credits' as const, perkValue: 10 },
  ]

  for (const milestone of streakThresholds) {
    const alreadyUnlocked = newUnlocked.some(u => u.id === milestone.id)
    const progressItem = newProgress.find(p => p.id === milestone.id)

    if (progressItem) {
      progressItem.current = achievement.stats.currentStreak
      if (!alreadyUnlocked && achievement.stats.currentStreak >= milestone.threshold) {
        progressItem.unlocked = true
        newUnlocked.push({
          id: milestone.id,
          name: milestone.name,
          description: `Completed tasks for ${milestone.threshold} consecutive days`,
          unlockedAt: new Date().toISOString(),
          perk: { type: milestone.perkType, value: milestone.perkValue },
        })
      }
    }
  }

  // Check focus achievements
  const focusProgressItem = newProgress.find(p => p.id === 'focus_50')
  if (focusProgressItem) {
    focusProgressItem.current = achievement.stats.focusCompletions
    const alreadyUnlocked = newUnlocked.some(u => u.id === 'focus_50')
    if (!alreadyUnlocked && achievement.stats.focusCompletions >= 50) {
      focusProgressItem.unlocked = true
      newUnlocked.push({
        id: 'focus_50',
        name: 'Focus Champion',
        description: 'Completed 50 tasks in focus mode',
        unlockedAt: new Date().toISOString(),
        perk: { type: 'daily_credits', value: 5 },
      })
    }
  }

  // Recalculate effective limits
  let maxTasksBonus = 0
  let dailyCreditsBonus = 0

  for (const unlocked of newUnlocked) {
    if (unlocked.perk?.type === 'max_tasks') {
      maxTasksBonus += unlocked.perk.value
    }
    if (unlocked.perk?.type === 'daily_credits') {
      dailyCreditsBonus += unlocked.perk.value
    }
  }

  return {
    ...achievement,
    unlocked: newUnlocked,
    progress: newProgress,
    effectiveLimits: {
      maxTasks: 100 + maxTasksBonus,
      maxNotes: 50,
      dailyAiCredits: 50 + dailyCreditsBonus,
    },
  }
}

// GET /api/achievements - Get user achievements
export const getAchievementsHandler = http.get('/api/achievements', async () => {
  await simulateLatency()

  // Recalculate streak before returning (in case time has passed)
  const currentStreak = calculateStreak(lastCompletionDate)
  achievement.stats.currentStreak = currentStreak

  return HttpResponse.json(achievement, { status: 200 })
})

// POST /api/achievements/task-completed - Update achievements when task completed
export const taskCompletedHandler = http.post(
  '/api/achievements/task-completed',
  async ({ request }) => {
    await simulateLatency()

    const body = await request.json()
    const { priority, focusMode } = body as { priority?: 'high' | 'medium' | 'low'; focusMode?: boolean }

    const today = new Date().toISOString().split('T')[0]

    // Update lifetime tasks
    achievement.stats.lifetimeTasksCompleted += 1

    // Update focus completions
    if (focusMode) {
      achievement.stats.focusCompletions += 1
    }

    // Update consistency streak
    if (lastCompletionDate !== today) {
      // First completion today
      const currentStreak = calculateStreak(lastCompletionDate)

      achievement.stats.currentStreak = currentStreak + 1
      lastCompletionDate = today

      // Update longest streak if needed
      if (achievement.stats.currentStreak > achievement.stats.longestStreak) {
        achievement.stats.longestStreak = achievement.stats.currentStreak
      }
    }

    // Check for achievement unlocks
    achievement = checkUnlocks(achievement)

    return HttpResponse.json(achievement, { status: 200 })
  }
)

// Export all achievement handlers
export const achievementsHandlers = [
  getAchievementsHandler,
  taskCompletedHandler,
]
