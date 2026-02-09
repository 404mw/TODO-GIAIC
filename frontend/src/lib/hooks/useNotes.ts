import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { NoteSchema, type Note } from '@/lib/schemas/note.schema';
import { z } from 'zod';

// Response schemas
const NoteListResponseSchema = z.object({
  data: z.array(NoteSchema),
});

const NoteResponseSchema = z.object({
  data: NoteSchema,
});

// Query hooks
export function useNotes(taskId?: string) {
  return useQuery({
    queryKey: taskId ? ['notes', 'task', taskId] : ['notes'],
    queryFn: () =>
      apiClient.get(
        taskId ? `/tasks/${taskId}/notes` : '/notes',
        NoteListResponseSchema
      ),
  });
}

export function useNote(noteId: string) {
  return useQuery({
    queryKey: ['notes', noteId],
    queryFn: () => apiClient.get(`/notes/${noteId}`, NoteResponseSchema),
    enabled: !!noteId,
  });
}

// Mutation hooks
export function useCreateNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (note: Partial<Note>) =>
      apiClient.post('/notes', note, NoteResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['notes', 'task', data.data.task_id] });
      }
    },
  });
}

export function useUpdateNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...note }: Partial<Note> & { id: string }) =>
      apiClient.put(`/notes/${id}`, note, NoteResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      queryClient.invalidateQueries({ queryKey: ['notes', data.data.id] });
      if (data.data.task_id) {
        queryClient.invalidateQueries({ queryKey: ['notes', 'task', data.data.task_id] });
      }
    },
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (noteId: string) =>
      apiClient.delete(`/notes/${noteId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}
