import { z } from 'zod';
import { SubtaskSourceSchema } from './common.schema';

/**
 * Subtask schema matching backend Subtask model.
 * Per data-model.md Entity 4 (FR-021)
 */
export const SubtaskSchema = z.object({
  id: z.string().uuid(),
  task_id: z.string().uuid(),

  // Subtask details
  title: z.string().min(1).max(200),

  // Completion tracking
  completed: z.boolean().default(false),
  completed_at: z.string().datetime().nullable(),

  // Ordering
  order_index: z.number().int().min(0),

  // Source tracking
  source: SubtaskSourceSchema.default('user'),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for creating a subtask
 */
export const CreateSubtaskRequestSchema = SubtaskSchema.pick({
  title: true,
  order_index: true,
}).partial({
  order_index: true,
});

/**
 * Request schema for updating a subtask
 */
export const UpdateSubtaskRequestSchema = SubtaskSchema.pick({
  title: true,
  completed: true,
  order_index: true,
}).partial();

// Type exports
export type Subtask = z.infer<typeof SubtaskSchema>;
export type CreateSubtaskRequest = z.infer<typeof CreateSubtaskRequestSchema>;
export type UpdateSubtaskRequest = z.infer<typeof UpdateSubtaskRequestSchema>;
