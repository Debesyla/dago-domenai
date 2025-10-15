#!/bin/bash
# v0.10 Database Migration and Cleanup Script
# 
# This script helps migrate to the v0.10 profile system and optionally
# clean the database for a fresh start.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}v0.10 Database Migration Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable not set${NC}"
    echo "Please set it with:"
    echo "  export DATABASE_URL='postgresql://user:password@localhost:5432/dbname'"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL found${NC}"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo ""
echo "1) Run migration only (preserve existing data)"
echo "2) Clean database and run migration (DESTRUCTIVE - removes all data)"
echo "3) Run migration validation only"
echo "4) Show current database stats"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Running v0.10 migration...${NC}"
        psql "$DATABASE_URL" -f db/migrations/v0.10_profile_system.sql
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Migration completed successfully${NC}"
            echo ""
            echo "Validating migration..."
            psql "$DATABASE_URL" -c "SELECT * FROM validate_profile_data();" -t
            echo ""
            echo -e "${GREEN}Migration complete!${NC}"
        else
            echo -e "${RED}✗ Migration failed${NC}"
            exit 1
        fi
        ;;
        
    2)
        echo -e "\n${RED}WARNING: This will DELETE ALL existing data!${NC}"
        echo "This includes:"
        echo "  - All domain analysis results"
        echo "  - All domain records"
        echo "  - All task records"
        echo "  - All discovery records"
        echo ""
        read -p "Are you ABSOLUTELY sure? Type 'yes' to continue: " confirm
        
        if [ "$confirm" != "yes" ]; then
            echo -e "${YELLOW}Aborted.${NC}"
            exit 0
        fi
        
        echo -e "\n${BLUE}Cleaning database...${NC}"
        
        # Clean up in correct order (respecting foreign keys)
        psql "$DATABASE_URL" << EOF
-- Drop views that depend on tables
DROP VIEW IF EXISTS profile_dependency_stats;
DROP VIEW IF EXISTS profile_combinations;
DROP VIEW IF EXISTS profile_execution_stats;
DROP VIEW IF EXISTS discovery_stats;
DROP VIEW IF EXISTS top_discovery_sources;

-- Truncate tables (CASCADE removes dependent data)
TRUNCATE results CASCADE;
TRUNCATE domain_discoveries CASCADE;
TRUNCATE domains CASCADE;
TRUNCATE tasks CASCADE;

SELECT 'Database cleaned' as status;
EOF
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Database cleaned${NC}"
        else
            echo -e "${RED}✗ Cleanup failed${NC}"
            exit 1
        fi
        
        echo -e "\n${BLUE}Running fresh migration...${NC}"
        psql "$DATABASE_URL" -f db/migrations/v0.10_profile_system.sql
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Migration completed successfully${NC}"
            echo ""
            echo "Validating migration..."
            psql "$DATABASE_URL" -c "SELECT * FROM validate_profile_data();" -t
            echo ""
            echo -e "${GREEN}Fresh database ready!${NC}"
        else
            echo -e "${RED}✗ Migration failed${NC}"
            exit 1
        fi
        ;;
        
    3)
        echo -e "\n${BLUE}Running migration validation...${NC}"
        psql "$DATABASE_URL" << EOF
SELECT 
    check_name,
    status,
    details
FROM validate_profile_data();
EOF
        ;;
        
    4)
        echo -e "\n${BLUE}Current Database Statistics:${NC}"
        echo ""
        psql "$DATABASE_URL" << EOF
-- Domain statistics
SELECT 'Total Domains' as metric, COUNT(*)::TEXT as value FROM domains
UNION ALL
SELECT 'Registered Domains', COUNT(*)::TEXT FROM domains WHERE is_registered = TRUE
UNION ALL
SELECT 'Active Domains', COUNT(*)::TEXT FROM domains WHERE is_active = TRUE
UNION ALL
SELECT 'Total Results', COUNT(*)::TEXT FROM results
UNION ALL
SELECT 'Total Tasks', COUNT(*)::TEXT FROM tasks
UNION ALL
SELECT 'Profile-based Tasks', COUNT(*)::TEXT FROM tasks WHERE task_type IN ('profile', 'meta')
UNION ALL
SELECT 'Legacy Tasks', COUNT(*)::TEXT FROM tasks WHERE task_type = 'legacy'
UNION ALL
SELECT 'Domain Discoveries', COUNT(*)::TEXT FROM domain_discoveries;
EOF
        
        echo ""
        echo -e "${BLUE}Task Types Distribution:${NC}"
        psql "$DATABASE_URL" << EOF
SELECT 
    task_type,
    COUNT(*) as count,
    array_agg(name) as task_names
FROM tasks
GROUP BY task_type
ORDER BY count DESC;
EOF
        
        echo ""
        echo -e "${BLUE}Profile Usage (if any):${NC}"
        psql "$DATABASE_URL" << EOF
SELECT 
    profiles_requested,
    COUNT(*) as usage_count
FROM results
WHERE profiles_requested IS NOT NULL
GROUP BY profiles_requested
ORDER BY usage_count DESC
LIMIT 10;
EOF
        ;;
        
    5)
        echo -e "${YELLOW}Exiting without changes.${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Done!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify migration: psql \$DATABASE_URL -c 'SELECT * FROM validate_profile_data();'"
echo "  2. View new meta profiles: psql \$DATABASE_URL -c 'SELECT name, profiles FROM tasks WHERE is_meta_profile = TRUE;'"
echo "  3. Run analysis with profiles: python -m src.orchestrator domains.txt --profiles quick-check"
echo ""
