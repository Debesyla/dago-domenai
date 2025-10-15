-- v0.10 - Composable Profile System Database Schema
-- This migration updates the tasks and results tables to support the new profile-based system

-- =============================================================================
-- TASKS TABLE UPDATES
-- =============================================================================

-- The tasks table previously stored rigid task names like 'basic-scan', 'full-scan'
-- With v0.10, we need to support flexible profile combinations
-- Instead of predefined tasks, we now have dynamic profile combinations

-- Add new columns to track profile-based execution
ALTER TABLE tasks 
ADD COLUMN IF NOT EXISTS task_type VARCHAR(50) DEFAULT 'legacy';  -- 'legacy', 'profile', 'meta'

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS profiles TEXT[];  -- Array of profile names used

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS is_meta_profile BOOLEAN DEFAULT FALSE;  -- Is this a meta profile?

COMMENT ON COLUMN tasks.task_type IS 'Type of task: legacy (old system), profile (specific profiles), meta (pre-configured combo)';
COMMENT ON COLUMN tasks.profiles IS 'Array of profile names used in this task (e.g., {dns,ssl,seo})';
COMMENT ON COLUMN tasks.is_meta_profile IS 'TRUE if this is a meta profile like quick-check or standard';

-- Create index for profile-based queries
CREATE INDEX IF NOT EXISTS idx_tasks_profiles ON tasks USING GIN(profiles);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);

-- =============================================================================
-- INSERT DEFAULT PROFILE-BASED TASKS
-- =============================================================================

-- Insert meta profiles as default tasks
INSERT INTO tasks (name, description, task_type, profiles, is_meta_profile) 
VALUES 
    ('quick-check', 'Fast filtering - registration + connectivity', 'meta', ARRAY['whois', 'http'], TRUE),
    ('standard', 'General analysis - core profiles + seo', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'seo'], TRUE),
    ('technical-audit', 'Security and infrastructure focus', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'headers', 'security', 'infrastructure', 'technology'], TRUE),
    ('business-research', 'Market intelligence', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'business', 'language', 'clustering'], TRUE),
    ('complete', 'Comprehensive analysis - all checks', 'meta', ARRAY['whois', 'dns', 'http', 'ssl', 'headers', 'content', 'infrastructure', 'technology', 'seo', 'security', 'compliance', 'business', 'language'], TRUE),
    ('monitor', 'Change detection - minimal recurring', 'meta', ARRAY['whois', 'http'], TRUE)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    task_type = EXCLUDED.task_type,
    profiles = EXCLUDED.profiles,
    is_meta_profile = EXCLUDED.is_meta_profile;

-- Mark existing legacy tasks
UPDATE tasks 
SET task_type = 'legacy' 
WHERE task_type IS NULL 
   OR name IN ('basic-scan', 'full-scan', 'research-scan');

-- =============================================================================
-- RESULTS TABLE UPDATES
-- =============================================================================

-- Add profile execution metadata to results
-- This helps track which profiles were actually executed and their performance

-- Add profile tracking columns
ALTER TABLE results
ADD COLUMN IF NOT EXISTS profiles_requested TEXT[];  -- Profiles requested by user

ALTER TABLE results
ADD COLUMN IF NOT EXISTS profiles_executed TEXT[];  -- Profiles actually executed (after dependency resolution)

ALTER TABLE results
ADD COLUMN IF NOT EXISTS execution_plan JSONB;  -- Full execution plan with dependencies

COMMENT ON COLUMN results.profiles_requested IS 'Array of profile names requested (e.g., {seo, headers})';
COMMENT ON COLUMN results.profiles_executed IS 'Array of profiles actually executed after dependency resolution (e.g., {http, content, headers, seo})';
COMMENT ON COLUMN results.execution_plan IS 'Complete execution plan with parallel groups, dependencies, and timing';

-- Create indexes for profile-based queries
CREATE INDEX IF NOT EXISTS idx_results_profiles_requested ON results USING GIN(profiles_requested);
CREATE INDEX IF NOT EXISTS idx_results_profiles_executed ON results USING GIN(profiles_executed);

-- =============================================================================
-- PROFILE EXECUTION STATISTICS VIEW
-- =============================================================================

-- View for analyzing profile usage and performance
CREATE OR REPLACE VIEW profile_execution_stats AS
SELECT 
    unnest(profiles_executed) as profile_name,
    COUNT(*) as times_executed,
    AVG(EXTRACT(EPOCH FROM (checked_at - d.created_at))) as avg_execution_time,
    MIN(checked_at) as first_used,
    MAX(checked_at) as last_used,
    COUNT(DISTINCT domain_id) as unique_domains
FROM results r
JOIN domains d ON r.domain_id = d.id
WHERE profiles_executed IS NOT NULL
GROUP BY profile_name
ORDER BY times_executed DESC;

COMMENT ON VIEW profile_execution_stats IS 'Statistics on profile usage and performance';

-- =============================================================================
-- PROFILE COMBINATION STATISTICS VIEW
-- =============================================================================

-- View for analyzing which profile combinations are most commonly used
CREATE OR REPLACE VIEW profile_combinations AS
SELECT 
    profiles_requested,
    COUNT(*) as usage_count,
    AVG(EXTRACT(EPOCH FROM (checked_at - d.created_at))) as avg_execution_time,
    MIN(checked_at) as first_used,
    MAX(checked_at) as last_used
FROM results r
JOIN domains d ON r.domain_id = d.id
WHERE profiles_requested IS NOT NULL
GROUP BY profiles_requested
ORDER BY usage_count DESC;

COMMENT ON VIEW profile_combinations IS 'Most commonly used profile combinations';

-- =============================================================================
-- PROFILE DEPENDENCY ANALYSIS VIEW
-- =============================================================================

-- View for analyzing how often dependencies are resolved
CREATE OR REPLACE VIEW profile_dependency_stats AS
SELECT 
    t.name as task_name,
    t.profiles as configured_profiles,
    COUNT(*) as execution_count,
    AVG(array_length(r.profiles_executed, 1)) as avg_profiles_executed,
    AVG(array_length(r.profiles_executed, 1) - array_length(t.profiles, 1)) as avg_dependencies_added
FROM results r
JOIN tasks t ON r.task_id = t.id
WHERE r.profiles_executed IS NOT NULL 
  AND t.profiles IS NOT NULL
GROUP BY t.name, t.profiles
ORDER BY execution_count DESC;

COMMENT ON VIEW profile_dependency_stats IS 'Analysis of dependency resolution effectiveness';

-- =============================================================================
-- MIGRATION VALIDATION
-- =============================================================================

-- Function to validate profile data consistency
CREATE OR REPLACE FUNCTION validate_profile_data()
RETURNS TABLE(
    check_name TEXT,
    status TEXT,
    details TEXT
) AS $$
BEGIN
    -- Check 1: Verify all tasks have task_type
    RETURN QUERY
    SELECT 
        'task_type_populated'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
        'Tasks without task_type: ' || COUNT(*)::TEXT
    FROM tasks WHERE task_type IS NULL;
    
    -- Check 2: Verify meta profiles have profiles array
    RETURN QUERY
    SELECT 
        'meta_profiles_have_profiles'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
        'Meta profiles without profiles array: ' || COUNT(*)::TEXT
    FROM tasks WHERE is_meta_profile = TRUE AND profiles IS NULL;
    
    -- Check 3: Verify results with profiles have execution data
    RETURN QUERY
    SELECT 
        'results_execution_consistency'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARN' END,
        'Results with requested but no executed profiles: ' || COUNT(*)::TEXT
    FROM results WHERE profiles_requested IS NOT NULL AND profiles_executed IS NULL;
    
    -- Check 4: Verify profile arrays are not empty
    RETURN QUERY
    SELECT 
        'non_empty_profile_arrays'::TEXT,
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
        'Tasks with empty profiles array: ' || COUNT(*)::TEXT
    FROM tasks WHERE profiles IS NOT NULL AND array_length(profiles, 1) = 0;
    
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_profile_data() IS 'Validates profile data consistency after migration';

-- =============================================================================
-- BACKWARD COMPATIBILITY NOTES
-- =============================================================================

-- This migration maintains backward compatibility:
-- 1. Old 'tasks' records are marked as task_type='legacy' and continue to work
-- 2. New profile-based tasks are added without removing old ones
-- 3. Results from old system don't need migration (profiles_* columns are nullable)
-- 4. Applications can gradually adopt profile system while old system still works

-- To verify migration success, run:
-- SELECT * FROM validate_profile_data();

-- =============================================================================
-- CLEANUP (Optional - use with caution)
-- =============================================================================

-- If you want to start fresh and remove all old data (DESTRUCTIVE - use carefully!):
-- TRUNCATE results CASCADE;  -- Removes all analysis results
-- DELETE FROM tasks WHERE task_type = 'legacy';  -- Removes legacy task definitions
-- This is useful for development but NOT recommended for production

-- =============================================================================
-- ROLLBACK SCRIPT (If needed)
-- =============================================================================

-- If you need to rollback this migration:
/*
DROP VIEW IF EXISTS profile_dependency_stats;
DROP VIEW IF EXISTS profile_combinations;
DROP VIEW IF EXISTS profile_execution_stats;
DROP FUNCTION IF EXISTS validate_profile_data();

ALTER TABLE results DROP COLUMN IF EXISTS execution_plan;
ALTER TABLE results DROP COLUMN IF EXISTS profiles_executed;
ALTER TABLE results DROP COLUMN IF EXISTS profiles_requested;

ALTER TABLE tasks DROP COLUMN IF EXISTS is_meta_profile;
ALTER TABLE tasks DROP COLUMN IF EXISTS profiles;
ALTER TABLE tasks DROP COLUMN IF EXISTS task_type;

DROP INDEX IF EXISTS idx_results_profiles_executed;
DROP INDEX IF EXISTS idx_results_profiles_requested;
DROP INDEX IF EXISTS idx_tasks_type;
DROP INDEX IF EXISTS idx_tasks_profiles;
*/
