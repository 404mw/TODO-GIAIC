import type { UserProfile } from '@/lib/schemas/user.schema'
import type { Achievement } from '@/lib/schemas/achievement.schema'

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
export const achievementFixture: Achievement = {
  id: 'aa0e8400-e29b-41d4-a716-446655440001',
  userId: '990e8400-e29b-41d4-a716-446655440001',
  highPrioritySlays: 12, // 12 high-priority tasks completed
  consistencyStreak: {
    currentStreak: 5, // 5 consecutive days
    longestStreak: 14, // Best streak was 14 days
    lastCompletionDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Yesterday (YYYY-MM-DD)
    graceDayUsed: false,
  },
  completionRatio: 67, // 67% completion ratio
  milestones: [
    {
      id: 'streak_7',
      name: 'Week Warrior',
      description: 'Completed tasks for 7 consecutive days',
      unlockedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'slays_10',
      name: 'Priority Master',
      description: 'Completed 10 high-priority tasks',
      unlockedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ],
  updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
}
