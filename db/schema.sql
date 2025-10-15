-- PostgreSQL schema for domenai project
-- Version: v0.10 (includes v0.8, v0.9, v0.10 migrations)
-- Last Updated: 2025-10-15

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Domains table (base + v0.8 flags)
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- v0.8: Early bailout flags
    is_registered BOOLEAN,
    is_active BOOLEAN
);

-- Create indexes for domain flags (v0.8)
CREATE INDEX IF NOT EXISTS idx_domains_is_registered ON domains(is_registered);
CREATE INDEX IF NOT EXISTS idx_domains_is_active ON domains(is_active);
CREATE INDEX IF NOT EXISTS idx_domains_status ON domains(is_registered, is_active) 
    WHERE is_registered = TRUE AND is_active = TRUE;

-- Tasks table (base + v0.10 profile system)
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    -- v0.10: Profile system fields
    task_type VARCHAR(50) DEFAULT 'legacy',
    profiles TEXT[],
    is_meta_profile BOOLEAN DEFAULT FALSE
);

-- Create indexes for tasks (v0.10)
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_profiles ON tasks USING gin(profiles);

-- Results table (base + v0.10 profile tracking)
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    checked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- v0.10: Profile execution tracking
    profiles_requested TEXT[],
    profiles_executed TEXT[],
    execution_plan JSONB
);

-- Create indexes for results profiles (v0.10)
CREATE INDEX IF NOT EXISTS idx_results_profiles_requested ON results USING gin(profiles_requested);
CREATE INDEX IF NOT EXISTS idx_results_profiles_executed ON results USING gin(profiles_executed);

-- Domain discoveries table (v0.9: redirect capture)
CREATE TABLE IF NOT EXISTS domain_discoveries (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    discovered_from VARCHAR(255) NOT NULL,
    discovery_method VARCHAR(50) NOT NULL DEFAULT 'redirect',
    discovered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for domain discoveries (v0.9)
CREATE INDEX IF NOT EXISTS idx_discoveries_domain_id ON domain_discoveries(domain_id);
CREATE INDEX IF NOT EXISTS idx_discoveries_source ON domain_discoveries(discovered_from);
CREATE INDEX IF NOT EXISTS idx_discoveries_method ON domain_discoveries(discovery_method);
CREATE INDEX IF NOT EXISTS idx_discoveries_date ON domain_discoveries(discovered_at);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Update updated_at timestamp on domains
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at on domains
DROP TRIGGER IF EXISTS trg_domains_updated_at ON domains;
CREATE TRIGGER trg_domains_updated_at
BEFORE UPDATE ON domains
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Function: Validate profile data consistency (v0.10)
CREATE OR REPLACE FUNCTION validate_profile_data()
RETURNS TABLE(check_name TEXT, status TEXT, details TEXT) AS $$
BEGIN
    -- Check 1: All tasks have task_type populated
    RETURN QUERY
    SELECT 
        'task_type_populated'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        'Tasks without task_type: ' || COUNT(*)::TEXT
    FROM tasks WHERE task_type IS NULL;

    -- Check 2: Meta profiles have profiles array
    RETURN QUERY
    SELECT 
        'meta_profiles_have_profiles'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        'Meta profiles without profiles array: ' || COUNT(*)::TEXT
    FROM tasks 
    WHERE is_meta_profile = TRUE 
    AND (profiles IS NULL OR array_length(profiles, 1) IS NULL);

    -- Check 3: Results with profile data consistency
    RETURN QUERY
    SELECT 
        'results_execution_consistency'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        'Results with requested but no executed profiles: ' || COUNT(*)::TEXT
    FROM results 
    WHERE profiles_requested IS NOT NULL 
    AND array_length(profiles_requested, 1) > 0
    AND (profiles_executed IS NULL OR array_length(profiles_executed, 1) IS NULL);

    -- Check 4: No empty profile arrays
    RETURN QUERY
    SELECT 
        'non_empty_profile_arrays'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END::TEXT,
        'Tasks with empty profiles array: ' || COUNT(*)::TEXT
    FROM tasks 
    WHERE profiles IS NOT NULL 
    AND array_length(profiles, 1) = 0;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- View: Discovery statistics (v0.9)
CREATE OR REPLACE VIEW v_discovery_stats AS
SELECT 
    discovery_method,
    COUNT(*) as total_discoveries,
    COUNT(DISTINCT domain_id) as unique_domains,
    COUNT(DISTINCT discovered_from) as unique_sources,
    MIN(discovered_at) as first_discovery,
    MAX(discovered_at) as last_discovery
FROM domain_discoveries
GROUP BY discovery_method;

-- View: Top discovery sources (v0.9)
CREATE OR REPLACE VIEW v_top_discovery_sources AS
SELECT 
    discovered_from as source_domain,
    discovery_method,
    COUNT(*) as domains_discovered,
    MAX(discovered_at) as last_discovery
FROM domain_discoveries
GROUP BY discovered_from, discovery_method
ORDER BY domains_discovered DESC;

-- View: Profile execution statistics (v0.10)
CREATE OR REPLACE VIEW v_profile_execution_stats AS
SELECT 
    unnest(profiles_executed) as profile_name,
    COUNT(*) as execution_count,
    COUNT(DISTINCT domain_id) as unique_domains,
    AVG(array_length(profiles_executed, 1)) as avg_profiles_per_execution,
    MIN(checked_at) as first_execution,
    MAX(checked_at) as last_execution
FROM results
WHERE profiles_executed IS NOT NULL
GROUP BY profile_name
ORDER BY execution_count DESC;

-- View: Profile combination patterns (v0.10)
CREATE OR REPLACE VIEW v_profile_combinations AS
SELECT 
    profiles_requested as profiles_combination,
    COUNT(*) as combination_count,
    COUNT(DISTINCT domain_id) as unique_domains,
    AVG(array_length(profiles_executed, 1)) as avg_executed_profiles,
    MAX(checked_at) as last_used
FROM results
WHERE profiles_requested IS NOT NULL
GROUP BY profiles_requested
ORDER BY combination_count DESC;

-- View: Profile dependency resolution stats (v0.10)
CREATE OR REPLACE VIEW v_profile_dependency_stats AS
SELECT 
    array_length(profiles_requested, 1) as requested_count,
    array_length(profiles_executed, 1) as executed_count,
    array_length(profiles_executed, 1) - array_length(profiles_requested, 1) as dependencies_added,
    COUNT(*) as occurrences
FROM results
WHERE profiles_requested IS NOT NULL 
AND profiles_executed IS NOT NULL
GROUP BY 
    array_length(profiles_requested, 1),
    array_length(profiles_executed, 1)
ORDER BY occurrences DESC;

-- ============================================================================
-- META PROFILES DATA (v0.10)
-- ============================================================================

-- Insert meta profiles (run only once, uses ON CONFLICT to prevent duplicates)
INSERT INTO tasks (name, description, task_type, profiles, is_meta_profile) VALUES
    ('quick-check', 'Fast filtering - registration + connectivity', 'meta', ARRAY['whois', 'http'], TRUE),
    ('standard', 'General analysis - core profiles + seo', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'seo'], TRUE),
    ('technical-audit', 'Security and infrastructure focus', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'headers', 'security', 'infrastructure', 'technology'], TRUE),
    ('business-research', 'Market intelligence', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'business', 'language', 'clustering'], TRUE),
    ('complete', 'Comprehensive analysis - all checks', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'headers', 'content', 'infrastructure', 'technology', 'seo', 'security', 'compliance', 'business', 'language'], TRUE),
    ('monitor', 'Change detection - minimal recurring', 'meta', ARRAY['whois', 'http'], TRUE)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- Migration History:
--   v0.8: Added is_registered, is_active flags to domains table
--   v0.9: Added domain_discoveries table and discovery views
--   v0.10: Added profile system (task_type, profiles, profile tracking in results)
--
-- To apply this schema to a fresh database:
--   psql $DATABASE_URL -f db/schema.sql
--
-- To migrate an existing database:
--   Use migration scripts in db/migrations/ directory
--   See db/migrations/README.md for details
--
-- ============================================================================
