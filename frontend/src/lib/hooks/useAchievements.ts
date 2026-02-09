import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { AchievementSchema, UserAchievementSchema } from '@/lib/schemas/achievement.schema';
import { z } from 'zod';

// Response schemas
const AchievementListResponseSchema = z.object({
  data: z.array(AchievementSchema),
});

const UserAchievementListResponseSchema = z.object({
  data: z.array(UserAchievementSchema),
});

// Query hooks
export function useAchievements() {
  return useQuery({
    queryKey: ['achievements'],
    queryFn: () => apiClient.get('/achievements', AchievementListResponseSchema),
  });
}

export function useUserAchievements(userId?: string) {
  return useQuery({
    queryKey: userId ? ['achievements', 'user', userId] : ['achievements', 'user', 'me'],
    queryFn: () =>
      apiClient.get(
        userId ? `/users/${userId}/achievements` : '/users/me/achievements',
        UserAchievementListResponseSchema
      ),
  });
}
