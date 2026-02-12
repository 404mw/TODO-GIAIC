-- Migration: Add created_at column to user_achievement_states table
-- This column was added to the TimestampMixin but not yet applied to production

-- Add created_at column with default value
ALTER TABLE user_achievement_states
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- For existing rows, set created_at to updated_at (best approximation)
UPDATE user_achievement_states
SET created_at = updated_at
WHERE created_at = NOW();

-- Verify the change
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_achievement_states'
AND column_name IN ('created_at', 'updated_at');
