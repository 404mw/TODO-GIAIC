import { z } from 'zod';
import { PrioritySchema, CompletedBySchema } from './common.schema';

/**
 * Task schema matching backend TaskInstance model.
 * Per data-model.md Entity 2 (FR-014)
 */
export const TaskSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  template_id: z.string().uuid().nullable(),

  // Task details
  title: z.string().min(1).max(200),
  message: z.string().max(2000).default(''),
  priority: PrioritySchema.default('medium'),
  due_date: z.string().datetime().nullable(),
  estimated_duration: z.number().int().min(1).max(720).nullable(),

  // Focus tracking
  focus_time_seconds: z.number().int().min(0).default(0),

  // Completion tracking
  completed: z.boolean().default(false),
  completed_at: z.string().datetime().nullable(),
  completed_by: CompletedBySchema.nullable(),

  // Status flags
  hidden: z.boolean().default(false),
  archived: z.boolean().default(false),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  version: z.number().int(),
});

/**
 * Task Template schema matching backend TaskTemplate model.
 * Per data-model.md Entity 3 (FR-015)
 */
export const TaskTemplateSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Template details
  title: z.string().min(1).max(200),
  message: z.string().max(2000).default(''),
  priority: PrioritySchema.default('medium'),
  estimated_duration: z.number().int().min(1).max(720).nullable(),

  // Recurrence
  rrule: z.string(),
  next_due: z.string().datetime().nullable(),
  active: z.boolean().default(true),

  // Timestamps
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Request schema for creating a task
 */
export const CreateTaskRequestSchema = TaskSchema.pick({
  title: true,
  message: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
}).partial({
  message: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
});

/**
 * Request schema for updating a task
 */
export const UpdateTaskRequestSchema = TaskSchema.pick({
  title: true,
  message: true,
  priority: true,
  due_date: true,
  estimated_duration: true,
  archived: true,
}).partial();

// Type exports
export type Task = z.infer<typeof TaskSchema>;
export type TaskTemplate = z.infer<typeof TaskTemplateSchema>;
export type CreateTaskRequest = z.infer<typeof CreateTaskRequestSchema>;
export type UpdateTaskRequest = z.infer<typeof UpdateTaskRequestSchema>;
