import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { AchievementDefinitionSchema, UserAchievementStateSchema } from '@/lib/schemas/achievement.schema';
import { z } from 'zod';

// Response schemas
const AchievementListResponseSchema = z.object({
  data: z.array(AchievementDefinitionSchema),
});

const UserAchievementStateResponseSchema = z.object({
  data: UserAchievementStateSchema,
});

// Query hooks
export function useAchievements() {
  return useQuery({
    queryKey: ['achievements', 'user', 'me'],
    queryFn: () => apiClient.get('/users/me/achievements', UserAchievementStateResponseSchema),
  });
}

export function useAchievementDefinitions() {
  return useQuery({
    queryKey: ['achievements', 'definitions'],
    queryFn: () => apiClient.get('/achievements', AchievementListResponseSchema),
  });
}

export function useUserAchievements(userId: string) {
  return useQuery({
    queryKey: ['achievements', 'user', userId],
    queryFn: () =>
      apiClient.get(`/users/${userId}/achievements`, UserAchievementStateResponseSchema),
  });
}
