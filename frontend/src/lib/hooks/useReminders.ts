import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ReminderSchema, type Reminder } from '@/lib/schemas/reminder.schema';
import { z } from 'zod';

// Response schemas
const ReminderListResponseSchema = z.object({
  data: z.array(ReminderSchema),
});

const ReminderResponseSchema = z.object({
  data: ReminderSchema,
});

// Query hooks
export function useReminders(taskId?: string) {
  return useQuery({
    queryKey: taskId ? ['reminders', 'task', taskId] : ['reminders'],
    queryFn: () =>
      apiClient.get(
        taskId ? `/tasks/${taskId}/reminders` : '/reminders',
        ReminderListResponseSchema
      ),
  });
}

export function useReminder(reminderId: string) {
  return useQuery({
    queryKey: ['reminders', reminderId],
    queryFn: () => apiClient.get(`/reminders/${reminderId}`, ReminderResponseSchema),
    enabled: !!reminderId,
  });
}

// Mutation hooks
export function useCreateReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reminder: Partial<Reminder>) =>
      apiClient.post('/reminders', reminder, ReminderResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['reminders', 'task', data.data.task_id] });
      }
    },
  });
}

export function useUpdateReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...reminder }: Partial<Reminder> & { id: string }) =>
      apiClient.put(`/reminders/${id}`, reminder, ReminderResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
      queryClient.invalidateQueries({ queryKey: ['reminders', data.data.id] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['reminders', 'task', data.data.task_id] });
      }
    },
  });
}

export function useDeleteReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reminderId: string) =>
      apiClient.delete(`/reminders/${reminderId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders'] });
    },
  });
}
