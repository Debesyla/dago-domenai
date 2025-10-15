# Database Migrations

This directory contains SQL migration scripts for the dago-domenai database schema.

## Migration History

| Version | File | Description | Status |
|---------|------|-------------|--------|
| v0.8 | `v0.8_add_domain_flags.sql` | Added is_registered and is_active flags to domains table | ✅ Complete |
| v0.9 | `v0.9_domain_discoveries.sql` | Added domain discovery tracking for redirect capture | ✅ Complete |
| v0.10 | `v0.10_profile_system.sql` | Updated tasks/results tables for composable profile system | ✅ Complete |

## Quick Start

### Running Migrations

**Option 1: Interactive Script (Recommended)**
```bash
export DATABASE_URL='postgresql://user:password@localhost:5432/domenai'
./migrate_v10.sh
```

**Option 2: Direct SQL Execution**
```bash
# Run specific migration
psql $DATABASE_URL -f migrations/v0.10_profile_system.sql

# Run all migrations in order
psql $DATABASE_URL -f migrations/v0.8_add_domain_flags.sql
psql $DATABASE_URL -f migrations/v0.9_domain_discoveries.sql
psql $DATABASE_URL -f migrations/v0.10_profile_system.sql
```

## Migration Details

### v0.8 - Domain Status Flags

**Purpose:** Enable early bailout optimization

**Changes:**
- Added `is_registered` column to `domains` table
- Added `is_active` column to `domains` table
- Created indexes for performance

**Impact:** Enables orchestrator to skip checks for unregistered/inactive domains

### v0.9 - Domain Discovery Tracking

**Purpose:** Track how domains are discovered through redirect capture

**Changes:**
- Created `domain_discoveries` table
- Added discovery tracking views
- Linked discoveries to source domains

**Impact:** Provides analytics on domain discovery patterns

### v0.10 - Composable Profile System

**Purpose:** Support flexible profile-based analysis

**Changes:**
- Updated `tasks` table with profile support
  - Added `task_type` (legacy/profile/meta)
  - Added `profiles` array
  - Added `is_meta_profile` flag
- Updated `results` table with profile tracking
  - Added `profiles_requested` array
  - Added `profiles_executed` array
  - Added `execution_plan` JSONB
- Created meta profile tasks (quick-check, standard, etc.)
- Added analytics views for profile usage

**Impact:** Enables profile-based execution with dependency resolution

## Validation

Each migration includes validation steps.

**Validate v0.10 Migration:**
```bash
psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
```

Expected output:
```
check_name                      | status | details
--------------------------------|--------|------------------------
task_type_populated             | PASS   | Tasks without task_type: 0
meta_profiles_have_profiles     | PASS   | Meta profiles without profiles array: 0
results_execution_consistency   | PASS   | Results with requested but no executed profiles: 0
non_empty_profile_arrays        | PASS   | Tasks with empty profiles array: 0
```

## Database Statistics

View current database state:
```bash
psql $DATABASE_URL << EOF
SELECT 'Total Domains' as metric, COUNT(*)::TEXT as value FROM domains
UNION ALL
SELECT 'Registered Domains', COUNT(*)::TEXT FROM domains WHERE is_registered = TRUE
UNION ALL
SELECT 'Active Domains', COUNT(*)::TEXT FROM domains WHERE is_active = TRUE
UNION ALL
SELECT 'Total Results', COUNT(*)::TEXT FROM results
UNION ALL
SELECT 'Profile-based Results', COUNT(*)::TEXT FROM results WHERE profiles_requested IS NOT NULL;
EOF
```

## Rolling Back

If you need to rollback a migration, each SQL file includes a rollback script at the end.

**Example: Rollback v0.10**
```sql
-- See bottom of v0.10_profile_system.sql for complete rollback script
DROP VIEW IF EXISTS profile_dependency_stats;
DROP VIEW IF EXISTS profile_combinations;
DROP VIEW IF EXISTS profile_execution_stats;
-- ... etc
```

**Note:** Rollback scripts are provided for emergency use only. Test thoroughly before rolling back production data.

## Best Practices

1. **Always backup before migrating:**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations on development first:**
   ```bash
   # Use a dev database
   export DATABASE_URL='postgresql://user:password@localhost:5432/domenai_dev'
   ./migrate_v10.sh
   ```

3. **Validate after migration:**
   ```bash
   psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
   ```

4. **Check application compatibility:**
   ```bash
   # Run tests
   python3 test_v10.py
   
   # Run sample analysis
   python -m src.orchestrator --domain example.lt --profiles quick-check
   ```

## Troubleshooting

### Issue: Migration fails with "relation already exists"

**Cause:** Migration already run or partial migration

**Solution:**
```bash
# Check what exists
psql $DATABASE_URL -c "\d tasks"
psql $DATABASE_URL -c "\d results"

# If columns exist, migration may be partially applied
# Run validation to check status
psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
```

### Issue: Foreign key constraint violation

**Cause:** Existing data inconsistencies

**Solution:**
```bash
# Check for orphaned records
psql $DATABASE_URL << EOF
SELECT 'Orphaned results' as issue, COUNT(*) 
FROM results r 
LEFT JOIN domains d ON r.domain_id = d.id 
WHERE d.id IS NULL;
EOF

# Clean up if needed (be careful!)
# DELETE FROM results WHERE domain_id NOT IN (SELECT id FROM domains);
```

### Issue: Permission denied

**Cause:** Database user lacks necessary permissions

**Solution:**
```bash
# Grant permissions (as superuser)
psql $DATABASE_URL << EOF
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
EOF
```

## Development vs Production

### Development
- Use `migrate_v10.sh` option 2 to clean and start fresh
- Recreate test data as needed
- Iterate quickly

### Production
- Always backup first
- Use `migrate_v10.sh` option 1 to preserve data
- Test on staging environment first
- Schedule during low-traffic window
- Have rollback plan ready

## Support

For issues or questions:
1. Check migration validation: `validate_profile_data()`
2. Review migration SQL comments for details
3. Check application logs for errors
4. Consult V10_COMPLETION.md for full documentation
