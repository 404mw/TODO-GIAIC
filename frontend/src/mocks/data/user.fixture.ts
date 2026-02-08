import type { UserProfile } from '@/lib/schemas/user.schema'
import type { AchievementResponse } from '@/lib/schemas/achievement.schema'

// Sample user fixture for MSW
export const userFixture: UserProfile = {
  id: '990e8400-e29b-41d4-a716-446655440001',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  preferences: {
    sidebarOpen: true,
    themeTweaks: {
      accentColor: '#3B82F6', // Blue
      glassIntensity: 0.15,
      animationSpeed: 1.0,
    },
  },
  firstLogin: false, // Set to true to trigger onboarding walkthrough
  tutorialCompleted: true,
  createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago
  updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
}

// Sample achievement fixture for MSW
export const achievementFixture: AchievementResponse = {
  stats: {
    lifetimeTasksCompleted: 42,
    currentStreak: 5,
    longestStreak: 14,
    focusCompletions: 18,
    notesConverted: 8,
  },
  unlocked: [
    {
      id: 'streak_7',
      name: 'Week Warrior',
      description: 'Completed tasks for 7 consecutive days',
      unlockedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      perk: {
        type: 'max_tasks',
        value: 10,
      },
    },
    {
      id: 'slays_10',
      name: 'Priority Master',
      description: 'Completed 10 high-priority tasks',
      unlockedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      perk: {
        type: 'daily_credits',
        value: 5,
      },
    },
  ],
  progress: [
    {
      id: 'streak_30',
      name: 'Monthly Maestro',
      current: 5,
      threshold: 30,
      unlocked: false,
    },
    {
      id: 'focus_50',
      name: 'Focus Champion',
      current: 18,
      threshold: 50,
      unlocked: false,
    },
  ],
  effectiveLimits: {
    maxTasks: 110, // Base 100 + 10 from perk
    maxNotes: 50,
    dailyAiCredits: 55, // Base 50 + 5 from perk
  },
}
