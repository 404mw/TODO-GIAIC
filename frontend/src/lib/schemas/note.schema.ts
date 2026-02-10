import { z } from 'zod';
import { TranscriptionStatusSchema } from './common.schema';

/**
 * Note schema matching backend Note model.
 * Per data-model.md Entity 5
 */
export const NoteSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Note content
  content: z.string().min(1).max(2000),

  // Archive status
  archived: z.boolean().default(false),

  // Voice recording fields (Pro only)
  voice_url: z.string().nullable(),
  voice_duration_seconds: z.number().int().min(1).max(300).nullable(),
  transcription_status: TranscriptionStatusSchema.nullable(),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for creating a note
 */
export const CreateNoteRequestSchema = NoteSchema.pick({
  content: true,
});

/**
 * Request schema for updating a note
 */
export const UpdateNoteRequestSchema = NoteSchema.pick({
  content: true,
  archived: true,
}).partial();

// Type exports
export type Note = z.infer<typeof NoteSchema>;
export type CreateNoteRequest = z.infer<typeof CreateNoteRequestSchema>;
export type UpdateNoteRequest = z.infer<typeof UpdateNoteRequestSchema>;
