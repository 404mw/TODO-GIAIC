-- Migration: Fix CreditOperation and CreditType enum case mismatch
--
-- Issue: PostgreSQL enum types were created with uppercase values (GRANT, CONSUME, etc.)
-- but the Python enums use lowercase values (grant, consume, etc.)
--
-- This migration converts the enum types to use lowercase values

-- Step 1: Convert operation column to text temporarily
ALTER TABLE ai_credit_ledger
ALTER COLUMN operation TYPE TEXT;

-- Step 2: Convert credit_type column to text temporarily
ALTER TABLE ai_credit_ledger
ALTER COLUMN credit_type TYPE TEXT;

-- Step 3: Drop the old enum types
DROP TYPE IF EXISTS creditoperation CASCADE;
DROP TYPE IF EXISTS credittype CASCADE;

-- Step 4: Create new enum types with lowercase values
CREATE TYPE creditoperation AS ENUM ('grant', 'consume', 'expire', 'carryover');
CREATE TYPE credittype AS ENUM ('kickstart', 'daily', 'subscription', 'purchased');

-- Step 5: Update existing data to lowercase (if any uppercase values exist)
UPDATE ai_credit_ledger SET operation = LOWER(operation);
UPDATE ai_credit_ledger SET credit_type = LOWER(credit_type);

-- Step 6: Convert columns back to enum types
ALTER TABLE ai_credit_ledger
ALTER COLUMN operation TYPE creditoperation USING operation::creditoperation;

ALTER TABLE ai_credit_ledger
ALTER COLUMN credit_type TYPE credittype USING credit_type::credittype;

-- Verify the changes
SELECT
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_name = 'ai_credit_ledger'
AND column_name IN ('operation', 'credit_type');
