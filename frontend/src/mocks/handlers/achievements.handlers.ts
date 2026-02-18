import { http, HttpResponse, delay } from 'msw'
import type { UserAchievementState, AchievementDefinition } from '@/lib/schemas/achievement.schema'

// Achievement definitions (all possible achievements)
const achievementDefinitions: AchievementDefinition[] = [
  {
    id: 'tasks_5',
    name: 'First Steps',
    message: 'Complete your first 5 tasks',
    category: 'tasks',
    threshold: 5,
    perk_type: 'max_tasks',
    perk_value: 10,
  },
  {
    id: 'tasks_10',
    name: 'Getting Started',
    message: 'Complete 10 tasks',
    category: 'tasks',
    threshold: 10,
    perk_type: 'max_tasks',
    perk_value: 25,
  },
  {
    id: 'tasks_25',
    name: 'Task Master',
    message: 'Complete 25 tasks',
    category: 'tasks',
    threshold: 25,
    perk_type: null,
    perk_value: null,
  },
  {
    id: 'tasks_50',
    name: 'Half Century',
    message: 'Complete 50 tasks',
    category: 'tasks',
    threshold: 50,
    perk_type: 'max_tasks',
    perk_value: 50,
  },
  {
    id: 'tasks_100',
    name: 'Century Club',
    message: 'Complete 100 tasks',
    category: 'tasks',
    threshold: 100,
    perk_type: 'daily_credits',
    perk_value: 25,
  },
  {
    id: 'streak_3',
    name: 'On Fire',
    message: 'Maintain a 3-day streak',
    category: 'streaks',
    threshold: 3,
    perk_type: null,
    perk_value: null,
  },
  {
    id: 'streak_7',
    name: 'Week Warrior',
    message: 'Maintain a 7-day streak',
    category: 'streaks',
    threshold: 7,
    perk_type: 'max_notes',
    perk_value: 10,
  },
  {
    id: 'streak_14',
    name: 'Fortnight Focus',
    message: 'Maintain a 14-day streak',
    category: 'streaks',
    threshold: 14,
    perk_type: 'max_notes',
    perk_value: 25,
  },
  {
    id: 'streak_30',
    name: 'Monthly Momentum',
    message: 'Maintain a 30-day streak',
    category: 'streaks',
    threshold: 30,
    perk_type: 'daily_credits',
    perk_value: 50,
  },
  {
    id: 'focus_5',
    name: 'Focus Novice',
    message: 'Complete 5 focus sessions',
    category: 'focus',
    threshold: 5,
    perk_type: null,
    perk_value: null,
  },
  {
    id: 'focus_10',
    name: 'Focus Apprentice',
    message: 'Complete 10 focus sessions',
    category: 'focus',
    threshold: 10,
    perk_type: 'daily_credits',
    perk_value: 10,
  },
  {
    id: 'notes_5',
    name: 'Note Taker',
    message: 'Convert 5 notes to tasks',
    category: 'notes',
    threshold: 5,
    perk_type: null,
    perk_value: null,
  },
]

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

// GET /api/v1/achievements - Get all achievement definitions
export const getAchievementDefinitionsHandler = http.get('/api/v1/achievements', async () => {
  await simulateLatency()
  return HttpResponse.json({ data: achievementDefinitions }, { status: 200 })
})

// GET /api/v1/achievements/me - Get user's achievement state
export const getUserAchievementsHandler = http.get('/api/v1/achievements/me', async () => {
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
  getAchievementDefinitionsHandler,
  getUserAchievementsHandler,
  taskCompletedHandler,
]
