import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { SubtaskSchema, type Subtask } from '@/lib/schemas/subtask.schema';
import { z } from 'zod';

// Response schemas
const SubtaskListResponseSchema = z.object({
  data: z.array(SubtaskSchema),
});

const SubtaskResponseSchema = z.object({
  data: SubtaskSchema,
});

// Query hooks
export function useSubtasks(taskId: string) {
  return useQuery({
    queryKey: ['subtasks', taskId],
    queryFn: () => apiClient.get(`/tasks/${taskId}/subtasks`, SubtaskListResponseSchema),
    enabled: !!taskId,
  });
}

// Mutation hooks
export function useCreateSubtask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, ...subtask }: Partial<Subtask> & { taskId: string }) =>
      apiClient.post(`/tasks/${taskId}/subtasks`, subtask, SubtaskResponseSchema),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', variables.task_id] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.task_id] });
    },
  });
}

export function useUpdateSubtask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, taskId, ...subtask }: Partial<Subtask> & { id: string; taskId: string }) =>
      apiClient.put(`/subtasks/${id}`, subtask, SubtaskResponseSchema),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', variables.task_id] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.task_id] });
    },
  });
}

export function useDeleteSubtask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, taskId }: { id: string; taskId: string }) =>
      apiClient.delete(`/subtasks/${id}`),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', variables.task_id] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.task_id] });
    },
  });
}

export function useCompleteSubtask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, taskId }: { id: string; taskId: string }) =>
      apiClient.post(`/subtasks/${id}/complete`, {}, SubtaskResponseSchema),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', variables.task_id] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.task_id] });
    },
  });
}
