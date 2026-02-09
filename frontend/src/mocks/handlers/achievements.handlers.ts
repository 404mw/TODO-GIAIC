import { http, HttpResponse, delay } from 'msw'
import type { Achievement } from '@/lib/schemas/achievement.schema'
import { achievementFixture } from '../data/user.fixture'

// In-memory storage (single achievement per user, using fixture data)
let achievement: Achievement = { ...achievementFixture }

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// Helper: Calculate streak from task completions
const calculateStreak = (lastCompletionDate: string | null, graceDayUsed: boolean): {
  currentStreak: number
  graceDayUsed: boolean
} => {
  if (!lastCompletionDate) {
    return { currentStreak: 0, graceDayUsed: false }
  }

  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  const lastDate = lastCompletionDate

  // If completed today, maintain streak
  if (lastDate === today) {
    return { currentStreak: achievement.consistencyStreak.currentStreak, graceDayUsed }
  }

  // If completed yesterday, maintain streak
  if (lastDate === yesterday) {
    return { currentStreak: achievement.consistencyStreak.currentStreak, graceDayUsed }
  }

  // If missed yesterday but haven't used grace day, use it
  const dayBeforeYesterday = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
    .toISOString()
    .split('T')[0]
  if (lastDate === dayBeforeYesterday && !graceDayUsed) {
    return { currentStreak: achievement.consistencyStreak.currentStreak, graceDayUsed: true }
  }

  // Streak is broken
  return { currentStreak: 0, graceDayUsed: false }
}

// Helper: Check and unlock milestones
const checkMilestones = (achievement: Achievement): Achievement => {
  const newMilestones = [...achievement.milestones]

  // Streak milestones
  const streakMilestones = [
    { id: 'streak_7', name: 'Week Warrior', threshold: 7 },
    { id: 'streak_14', name: 'Fortnight Champion', threshold: 14 },
    { id: 'streak_30', name: 'Monthly Master', threshold: 30 },
  ]

  for (const milestone of streakMilestones) {
    const alreadyUnlocked = newMilestones.some(m => m.id === milestone.id)
    if (!alreadyUnlocked && achievement.consistencyStreak.currentStreak >= milestone.threshold) {
      newMilestones.push({
        id: milestone.id,
        name: milestone.name,
        description: `Completed tasks for ${milestone.threshold} consecutive days`,
        unlockedAt: new Date().toISOString(),
      })
    }
  }

  // High-priority slays milestones
  const slaysMilestones = [
    { id: 'slays_10', name: 'Priority Master', threshold: 10 },
    { id: 'slays_25', name: 'Priority Veteran', threshold: 25 },
    { id: 'slays_50', name: 'Priority Legend', threshold: 50 },
  ]

  for (const milestone of slaysMilestones) {
    const alreadyUnlocked = newMilestones.some(m => m.id === milestone.id)
    if (!alreadyUnlocked && achievement.highPrioritySlays >= milestone.threshold) {
      newMilestones.push({
        id: milestone.id,
        name: milestone.name,
        description: `Completed ${milestone.threshold} high-priority tasks`,
        unlockedAt: new Date().toISOString(),
      })
    }
  }

  return { ...achievement, milestones: newMilestones }
}

// GET /api/achievements - Get user achievements
export const getAchievementsHandler = http.get('/api/achievements', async () => {
  await simulateLatency()

  // Recalculate streak before returning (in case time has passed)
  const { currentStreak, graceDayUsed } = calculateStreak(
    achievement.consistencyStreak.lastCompletionDate,
    achievement.consistencyStreak.graceDayUsed
  )

  achievement.consistencyStreak.currentStreak = currentStreak
  achievement.consistencyStreak.graceDayUsed = graceDayUsed

  return HttpResponse.json(achievement, { status: 200 })
})

// POST /api/achievements/task-completed - Update achievements when task completed
export const taskCompletedHandler = http.post(
  '/api/achievements/task-completed',
  async ({ request }) => {
    await simulateLatency()

    const body = await request.json()
    const { priority } = body as { priority?: 'high' | 'medium' | 'low' }

    const today = new Date().toISOString().split('T')[0]
    const lastDate = achievement.consistencyStreak.lastCompletionDate

    // Update high-priority slays
    if (priority === 'high') {
      achievement.highPrioritySlays += 1
    }

    // Update consistency streak
    if (lastDate !== today) {
      // First completion today
      const { currentStreak, graceDayUsed } = calculateStreak(
        lastDate,
        achievement.consistencyStreak.graceDayUsed
      )

      achievement.consistencyStreak.currentStreak = currentStreak + 1
      achievement.consistencyStreak.graceDayUsed = graceDayUsed
      achievement.consistencyStreak.lastCompletionDate = today

      // Update longest streak if needed
      if (
        achievement.consistencyStreak.currentStreak >
        achievement.consistencyStreak.longestStreak
      ) {
        achievement.consistencyStreak.longestStreak =
          achievement.consistencyStreak.currentStreak
      }
    }

    // Check for milestone unlocks
    achievement = checkMilestones(achievement)

    // Update timestamp
    achievement.updated_at = new Date().toISOString()

    return HttpResponse.json(achievement, { status: 200 })
  }
)

// PATCH /api/achievements/completion-ratio - Update completion ratio
export const updateCompletionRatioHandler = http.patch(
  '/api/achievements/completion-ratio',
  async ({ request }) => {
    await simulateLatency()

    const body = await request.json()
    const { completionRatio } = body as { completionRatio: number }

    if (completionRatio < 0 || completionRatio > 100) {
      return HttpResponse.json(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Completion ratio must be between 0 and 100',
          },
        },
        { status: 400 }
      )
    }

    achievement.completionRatio = completionRatio
    achievement.updated_at = new Date().toISOString()

    return HttpResponse.json(achievement, { status: 200 })
  }
)

// Export all achievement handlers
export const achievementsHandlers = [
  getAchievementsHandler,
  taskCompletedHandler,
  updateCompletionRatioHandler,
]
