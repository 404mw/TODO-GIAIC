import { z } from 'zod';
import { EntityTypeSchema, ActivitySourceSchema } from './common.schema';

/**
 * Activity Log schema matching backend ActivityLog model.
 * Per data-model.md Entity 11 (FR-052)
 */
export const ActivityLogSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),

  // Entity reference
  entity_type: EntityTypeSchema,
  entity_id: z.string().uuid(),

  // Action details
  action: z.string(),
  source: ActivitySourceSchema,

  // Additional context
  extra_data: z.record(z.any()).default({}),
  request_id: z.string().uuid().nullable(),

  // Timestamp
  created_at: z.string().datetime(),
});

/**
 * Activity log response for listing
 */
export const ActivityLogListSchema = z.array(ActivityLogSchema);

// Type exports
export type ActivityLog = z.infer<typeof ActivityLogSchema>;
export type ActivityLogList = z.infer<typeof ActivityLogListSchema>;
