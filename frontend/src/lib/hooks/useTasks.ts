import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { TaskSchema, type Task } from '@/lib/schemas/task.schema';
import { z } from 'zod';

// Response schemas
const TaskListResponseSchema = z.object({
  data: z.array(TaskSchema),
});

const TaskResponseSchema = z.object({
  data: TaskSchema,
});

const TaskCompletionResponseSchema = z.object({
  task: TaskSchema,
});

// Query hooks
export function useTasks(filters?: { completed?: boolean; priority?: string; enabled?: boolean }) {
  const params = new URLSearchParams();
  if (filters?.completed !== undefined) params.set('completed', String(filters.completed));
  if (filters?.priority) params.set('priority', filters.priority);
  const queryString = params.toString();

  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => apiClient.get(`/tasks${queryString ? `?${queryString}` : ''}`, TaskListResponseSchema),
    enabled: filters?.enabled ?? true, // Default to enabled
  });
}

export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => apiClient.get(`/tasks/${taskId}`, TaskResponseSchema),
    enabled: !!taskId,
  });
}

// Mutation hooks
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: Partial<Task>) =>
      apiClient.post('/tasks', task, TaskResponseSchema),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...task }: Partial<Task> & { id: string }) =>
      apiClient.put(`/tasks/${id}`, task, TaskResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', data.data.id] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      apiClient.delete(`/tasks/${taskId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      apiClient.post(`/tasks/${taskId}/complete`, {}, TaskCompletionResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', data.task.id] });
    },
  });
}

export function useAutoCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      apiClient.post(`/tasks/${taskId}/auto-complete`, {}, TaskCompletionResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', data.task.id] });
    },
  });
}
