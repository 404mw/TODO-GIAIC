import { http, HttpResponse, delay } from 'msw'
import type { UserAchievementState } from '@/lib/schemas/achievement.schema'

// In-memory storage for user achievement state
let achievementState: UserAchievementState = {
  id: 'aa0e8400-e29b-41d4-a716-446655440001',
  user_id: '990e8400-e29b-41d4-a716-446655440001',
  lifetime_tasks_completed: 42,
  current_streak: 5,
  longest_streak: 14,
  last_completion_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  focus_completions: 8,
  notes_converted: 3,
  unlocked_achievements: ['tasks_5', 'tasks_10', 'streak_7'],
  created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
}

// Helper: Simulate network latency
const simulateLatency = () => delay(Math.floor(Math.random() * (500 - 100 + 1)) + 100)

// GET /api/achievements - Get user achievements
export const getAchievementsHandler = http.get('/api/achievements', async () => {
  await simulateLatency()
  return HttpResponse.json({ data: achievementState }, { status: 200 })
})

// POST /api/achievements/task-completed - Update achievements when task completed
export const taskCompletedHandler = http.post(
  '/api/achievements/task-completed',
  async () => {
    await simulateLatency()

    // Update stats
    achievementState.lifetime_tasks_completed += 1
    const today = new Date().toISOString().split('T')[0]

    if (achievementState.last_completion_date !== today) {
      achievementState.current_streak += 1
      achievementState.last_completion_date = today

      if (achievementState.current_streak > achievementState.longest_streak) {
        achievementState.longest_streak = achievementState.current_streak
      }
    }

    achievementState.updated_at = new Date().toISOString()

    return HttpResponse.json({ data: achievementState }, { status: 200 })
  }
)

// Export all achievement handlers
export const achievementsHandlers = [
  getAchievementsHandler,
  taskCompletedHandler,
]
