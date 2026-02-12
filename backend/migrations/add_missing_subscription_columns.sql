-- Migration: Add missing columns to subscriptions table
--
-- Issue: Production database missing columns that the Subscription model expects
-- Error: column subscriptions.retry_count does not exist
--
-- This migration adds all potentially missing payment tracking columns

-- Add retry_count column
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;

-- Add last_retry_at column
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS last_retry_at TIMESTAMPTZ;

-- Add last_payment_at column
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS last_payment_at TIMESTAMPTZ;

-- Add grace_warning_sent column
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS grace_warning_sent BOOLEAN NOT NULL DEFAULT false;

-- Verify the changes
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'subscriptions'
AND column_name IN ('retry_count', 'last_retry_at', 'last_payment_at', 'grace_warning_sent')
ORDER BY column_name;
