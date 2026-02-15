import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import {
  AchievementDefinitionSchema,
  AchievementDataSchema,
} from '@/lib/schemas/achievement.schema';
import { z } from 'zod';

// Response schemas
const AchievementListResponseSchema = z.object({
  data: z.array(AchievementDefinitionSchema),
});

const AchievementDataResponseSchema = z.object({
  data: AchievementDataSchema,
});

// Query hooks
export function useAchievements() {
  return useQuery({
    queryKey: ['achievements', 'user', 'me'],
    queryFn: () => apiClient.get('/achievements/me', AchievementDataResponseSchema),
  });
}

export function useAchievementDefinitions() {
  return useQuery({
    queryKey: ['achievements', 'definitions'],
    queryFn: () => apiClient.get('/achievements', AchievementListResponseSchema),
    staleTime: 1000 * 60 * 60, // 1 hour - achievement definitions rarely change
    gcTime: 1000 * 60 * 60 * 24, // 24 hours cache
  });
}

export function useUserAchievements(userId: string) {
  return useQuery({
    queryKey: ['achievements', 'user', userId],
    queryFn: () =>
      apiClient.get(`/users/${userId}/achievements`, AchievementDataResponseSchema),
  });
}
