import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ActivityLogSchema } from '@/lib/schemas/activity.schema';
import { z } from 'zod';

const ActivityListResponseSchema = z.object({
  data: z.array(ActivityLogSchema),
});

export function useActivityLog(limit = 50) {
  return useQuery({
    queryKey: ['activity', { limit }],
    queryFn: () => apiClient.get(`/activity?limit=${limit}`, ActivityListResponseSchema),
  });
}

export function useUserActivity(userId: string) {
  return useQuery({
    queryKey: ['activity', 'user', userId],
    queryFn: () => apiClient.get(`/users/${userId}/activity`, ActivityListResponseSchema),
    enabled: !!userId,
  });
}
