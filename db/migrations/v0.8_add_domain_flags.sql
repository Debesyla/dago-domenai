-- Migration for v0.8: Add domain status flags
-- Adds is_registered and is_active columns to domains table

-- Add is_registered column
ALTER TABLE domains 
ADD COLUMN IF NOT EXISTS is_registered BOOLEAN DEFAULT NULL;

-- Add is_active column
ALTER TABLE domains 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT NULL;

-- Add comments for documentation
COMMENT ON COLUMN domains.is_registered IS 
'Domain registration status: TRUE=registered, FALSE=not registered, NULL=not checked';

COMMENT ON COLUMN domains.is_active IS 
'Domain activity status: TRUE=has active website, FALSE=inactive/redirects away, NULL=not checked or not applicable';

-- Create index for querying by status
CREATE INDEX IF NOT EXISTS idx_domains_is_registered ON domains(is_registered);
CREATE INDEX IF NOT EXISTS idx_domains_is_active ON domains(is_active);

-- Create index for common queries (active registered domains)
CREATE INDEX IF NOT EXISTS idx_domains_status ON domains(is_registered, is_active) 
WHERE is_registered = TRUE AND is_active = TRUE;
