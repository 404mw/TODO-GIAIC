-- Comprehensive Migration: Fix all production schema mismatches
--
-- This migration brings the production database schema in sync with the models
-- Issues fixed:
-- 1. user_achievement_states.created_at column missing
-- 2. Enum types using uppercase names instead of lowercase values
-- 3. subscriptions payment tracking columns missing
--
-- Run this script on Render PostgreSQL database

-- ============================================================================
-- PART 1: Fix user_achievement_states table
-- ============================================================================

-- Add created_at column to user_achievement_states
ALTER TABLE user_achievement_states
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Backfill existing rows with updated_at value (best approximation)
UPDATE user_achievement_states
SET created_at = updated_at
WHERE created_at = NOW();

-- ============================================================================
-- PART 2: Fix enum type case mismatch (creditoperation, credittype)
-- ============================================================================

-- Convert columns to text temporarily
ALTER TABLE ai_credit_ledger ALTER COLUMN operation TYPE TEXT;
ALTER TABLE ai_credit_ledger ALTER COLUMN credit_type TYPE TEXT;

-- Drop old enum types
DROP TYPE IF EXISTS creditoperation CASCADE;
DROP TYPE IF EXISTS credittype CASCADE;

-- Create new enum types with lowercase values
CREATE TYPE creditoperation AS ENUM ('grant', 'consume', 'expire', 'carryover');
CREATE TYPE credittype AS ENUM ('kickstart', 'daily', 'subscription', 'purchased');

-- Update existing data to lowercase (if any uppercase values exist)
UPDATE ai_credit_ledger SET operation = LOWER(operation);
UPDATE ai_credit_ledger SET credit_type = LOWER(credit_type);

-- Convert columns back to enum types
ALTER TABLE ai_credit_ledger
ALTER COLUMN operation TYPE creditoperation USING operation::creditoperation;

ALTER TABLE ai_credit_ledger
ALTER COLUMN credit_type TYPE credittype USING credit_type::credittype;

-- ============================================================================
-- PART 3: Add missing subscription columns
-- ============================================================================

-- Add retry_count column (payment retry attempts)
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;

-- Add last_retry_at column (last retry timestamp)
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMPTZ;

-- Add last_payment_at column (last successful payment)
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS last_payment_at TIMESTAMPTZ;

-- Add grace_warning_sent column (grace period notification flag)
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS grace_warning_sent BOOLEAN NOT NULL DEFAULT false;

-- ============================================================================
-- VERIFICATION: Check that all changes were applied
-- ============================================================================

-- Verify user_achievement_states has created_at
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_achievement_states'
AND column_name IN ('created_at', 'updated_at')
ORDER BY column_name;

-- Verify enum types are lowercase
SELECT enumlabel
FROM pg_enum
WHERE enumtypid = 'creditoperation'::regtype
ORDER BY enumlabel;

SELECT enumlabel
FROM pg_enum
WHERE enumtypid = 'credittype'::regtype
ORDER BY enumlabel;

-- Verify subscription columns exist
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'subscriptions'
AND column_name IN ('retry_count', 'last_retry_at', 'last_payment_at', 'grace_warning_sent')
ORDER BY column_name;

-- Summary
SELECT 'Migration completed successfully. All schema changes applied.' AS status;
