import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { FocusSessionSchema, type FocusSession } from '@/lib/schemas/focus.schema';
import { z } from 'zod';

// Response schemas
const FocusSessionListResponseSchema = z.object({
  data: z.array(FocusSessionSchema),
});

const FocusSessionResponseSchema = z.object({
  data: FocusSessionSchema,
});

// Query hooks
export function useFocusSessions(taskId?: string) {
  return useQuery({
    queryKey: taskId ? ['focus', 'task', taskId] : ['focus'],
    queryFn: () =>
      apiClient.get(
        taskId ? `/tasks/${taskId}/focus-sessions` : '/focus-sessions',
        FocusSessionListResponseSchema
      ),
  });
}

export function useActiveFocusSession() {
  return useQuery({
    queryKey: ['focus', 'active'],
    queryFn: () => apiClient.get('/focus-sessions/active', FocusSessionResponseSchema),
    retry: false, // Don't retry if no active session
  });
}

// Mutation hooks
export function useCreateFocusSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (session: Partial<FocusSession>) =>
      apiClient.post('/focus-sessions', session, FocusSessionResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['focus'] });
      queryClient.invalidateQueries({ queryKey: ['focus', 'active'] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['focus', 'task', data.data.task_id] });
      }
    },
  });
}

export function useEndFocusSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) =>
      apiClient.post(`/focus-sessions/${sessionId}/end`, {}, FocusSessionResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['focus'] });
      queryClient.invalidateQueries({ queryKey: ['focus', 'active'] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['focus', 'task', data.data.task_id] });
        queryClient.invalidateQueries({ queryKey: ['tasks', data.data.task_id] });
      }
    },
  });
}
