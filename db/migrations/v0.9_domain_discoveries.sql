-- v0.9 - Domain Discoveries Tracking
-- This migration adds tracking for how domains are discovered through redirect capture

-- Domain discoveries table
-- Tracks when and how new domains are discovered
CREATE TABLE IF NOT EXISTS domain_discoveries (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    discovered_from VARCHAR(255) NOT NULL,  -- Source domain that led to discovery
    discovery_method VARCHAR(50) NOT NULL DEFAULT 'redirect',  -- How it was discovered
    discovered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Additional metadata
    metadata JSONB,  -- Store additional context (redirect chain, HTTP status, etc.)
    
    CONSTRAINT fk_domain_discoveries_domain FOREIGN KEY (domain_id) REFERENCES domains(id)
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_discoveries_domain_id ON domain_discoveries(domain_id);
CREATE INDEX IF NOT EXISTS idx_discoveries_source ON domain_discoveries(discovered_from);
CREATE INDEX IF NOT EXISTS idx_discoveries_method ON domain_discoveries(discovery_method);
CREATE INDEX IF NOT EXISTS idx_discoveries_date ON domain_discoveries(discovered_at);

-- Comment the table
COMMENT ON TABLE domain_discoveries IS 'Tracks how and when domains are discovered through redirect capture and other methods';
COMMENT ON COLUMN domain_discoveries.domain_id IS 'Reference to the discovered domain';
COMMENT ON COLUMN domain_discoveries.discovered_from IS 'Source domain that redirected to the discovered domain';
COMMENT ON COLUMN domain_discoveries.discovery_method IS 'Method of discovery: redirect, link, user_submission, etc.';
COMMENT ON COLUMN domain_discoveries.discovered_at IS 'Timestamp when domain was discovered';
COMMENT ON COLUMN domain_discoveries.metadata IS 'Additional context about the discovery (redirect chain, status codes, etc.)';

-- View for discovery statistics
CREATE OR REPLACE VIEW discovery_stats AS
SELECT 
    d.domain_name as discovered_domain,
    dd.discovered_from as source_domain,
    dd.discovery_method,
    dd.discovered_at,
    dd.metadata->>'status_code' as status_code,
    dd.metadata->>'redirect_count' as redirect_hops
FROM domain_discoveries dd
JOIN domains d ON dd.domain_id = d.id
ORDER BY dd.discovered_at DESC;

COMMENT ON VIEW discovery_stats IS 'Convenient view for analyzing domain discoveries';

-- View for top discovery sources (hub domains)
CREATE OR REPLACE VIEW top_discovery_sources AS
SELECT 
    discovered_from as source_domain,
    COUNT(*) as domains_discovered,
    MIN(discovered_at) as first_discovery,
    MAX(discovered_at) as latest_discovery
FROM domain_discoveries
GROUP BY discovered_from
ORDER BY domains_discovered DESC;

COMMENT ON VIEW top_discovery_sources IS 'Domains that have led to the most discoveries (hub domains)';
