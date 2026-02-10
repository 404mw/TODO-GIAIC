import { useEffect, useRef } from 'react'
import { useAchievements, useAchievementDefinitions } from './useAchievements'
import { useNotificationStore } from '@/lib/stores/notification.store'

/**
 * Hook to listen for achievement unlocks and show notifications
 *
 * Usage:
 * ```tsx
 * useAchievementNotifications()
 * ```
 *
 * Features:
 * - Detects newly unlocked achievements
 * - Shows toast notification with achievement name and perk
 * - Adds to notification center
 * - Prevents duplicate notifications on mount
 */
export function useAchievementNotifications() {
  const { data: userStateResponse } = useAchievements()
  const { data: definitionsResponse } = useAchievementDefinitions()
  const addNotification = useNotificationStore((state) => state.addNotification)

  // Track previous unlocked achievements to detect new unlocks
  const previousUnlockedRef = useRef<Set<string>>(new Set())
  const isInitialMount = useRef(true)

  useEffect(() => {
    const unlockedIds = userStateResponse?.data?.unlocked_achievements || []
    const definitions = definitionsResponse?.data || []

    // On initial mount, just store the current state without notifying
    if (isInitialMount.current) {
      previousUnlockedRef.current = new Set(unlockedIds)
      isInitialMount.current = false
      return
    }

    // Find newly unlocked achievements
    const newlyUnlocked = unlockedIds.filter(
      (id) => !previousUnlockedRef.current.has(id)
    )

    // Show notification for each newly unlocked achievement
    newlyUnlocked.forEach((achievementId) => {
      const achievement = definitions.find((def) => def.id === achievementId)
      if (!achievement) return

      // Build notification message
      let message = achievement.message

      // Add perk info if available
      if (achievement.perk_type && achievement.perk_value) {
        message += ` | Reward: +${achievement.perk_value} ${achievement.perk_type.replace('_', ' ')}`
      }

      // Show toast notification
      addNotification({
        type: 'success',
        title: `🏆 Achievement Unlocked: ${achievement.name}`,
        message,
      })
    })

    // Update previous unlocked set
    previousUnlockedRef.current = new Set(unlockedIds)
  }, [userStateResponse, definitionsResponse, addNotification])
}
