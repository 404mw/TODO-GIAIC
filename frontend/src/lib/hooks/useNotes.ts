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

/**
 * T125 — Notes are standalone entities (UPDATE-02).
 * Queries GET /api/v1/notes — no taskId param.
 * archived=true for archived notes.
 */
export function useNotes(options?: { archived?: boolean; enabled?: boolean }) {
  const params = new URLSearchParams();
  if (options?.archived) params.set('archived', 'true');
  const queryString = params.toString();

  return useQuery({
    queryKey: ['notes', options],
    queryFn: () =>
      apiClient.get(
        `/notes${queryString ? `?${queryString}` : ''}`,
        NoteListResponseSchema
      ),
    enabled: options?.enabled ?? true,
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

/**
 * T125 — Create note: POST /api/v1/notes (standalone, no taskId).
 */
export function useCreateNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (note: Partial<Note>) =>
      apiClient.post('/notes', note, NoteResponseSchema),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
    },
  });
}

/**
 * T125 — Update note: PATCH /api/v1/notes/${noteId} (not PUT).
 */
export function useUpdateNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, ...note }: Partial<Note> & { id: string }) =>
      apiClient.patch(`/notes/${id}`, note, NoteResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      queryClient.invalidateQueries({ queryKey: ['notes', data.data.id] });
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

export function useArchiveNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id }: { id: string }) =>
      apiClient.patch(`/notes/${id}`, { archived: true }, NoteResponseSchema),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      queryClient.invalidateQueries({ queryKey: ['notes', data.data.id] });
    },
  });
}
