#!/bin/bash
# Database Setup Script for dago-domenai
# Version: v1.0
# 
# This script initializes a fresh database with the complete v1.0 schema.
# For production use, not for migrations (we start fresh at v1.0).

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║      Database Setup - dago-domenai v1.0               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Load environment variables
if [ -f .env ]; then
    source .env
    echo -e "${GREEN}✓${NC} Loaded .env file"
else
    echo -e "${RED}✗${NC} .env file not found"
    echo ""
    echo "Create a .env file with:"
    echo "  DATABASE_URL=postgresql://user:pass@host:port/dbname"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}✗${NC} DATABASE_URL not set in .env"
    exit 1
fi

echo -e "${GREEN}✓${NC} Database URL configured"
echo ""

# Show menu
echo "Select an option:"
echo ""
echo "  1) Initialize fresh database (DESTRUCTIVE - drops all data)"
echo "  2) Verify existing database"
echo "  3) Show database statistics"
echo "  4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}WARNING:${NC} This will DROP ALL existing tables and data!"
        echo ""
        read -p "Are you sure? Type 'yes' to continue: " confirm
        
        if [ "$confirm" != "yes" ]; then
            echo "Aborted."
            exit 0
        fi
        
        echo ""
        echo -e "${BLUE}Dropping existing schema...${NC}"
        psql $DATABASE_URL <<EOF
-- Drop all tables (cascades to all dependent objects)
DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS domains CASCADE;
DROP TABLE IF EXISTS domain_discoveries CASCADE;

-- Drop all views
DROP VIEW IF EXISTS v_discovery_stats CASCADE;
DROP VIEW IF EXISTS v_top_discovery_sources CASCADE;
DROP VIEW IF EXISTS v_profile_execution_stats CASCADE;
DROP VIEW IF EXISTS v_profile_combinations CASCADE;
DROP VIEW IF EXISTS v_profile_dependency_stats CASCADE;

-- Drop all functions
DROP FUNCTION IF EXISTS set_updated_at() CASCADE;
DROP FUNCTION IF EXISTS validate_profile_data() CASCADE;
EOF
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Existing schema dropped"
        else
            echo -e "${RED}✗${NC} Failed to drop schema"
            exit 1
        fi
        
        echo ""
        echo -e "${BLUE}Creating fresh schema from db/schema.sql...${NC}"
        psql $DATABASE_URL -f db/schema.sql > /dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Schema created successfully"
        else
            echo -e "${RED}✗${NC} Failed to create schema"
            exit 1
        fi
        
        echo ""
        echo -e "${BLUE}Running validation...${NC}"
        psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();" -t
        
        echo ""
        echo -e "${GREEN}✓${NC} Database initialized successfully!"
        echo ""
        echo "Summary:"
        psql $DATABASE_URL <<EOF
SELECT 
    (SELECT COUNT(*) FROM domains) as domains,
    (SELECT COUNT(*) FROM tasks) as tasks,
    (SELECT COUNT(*) FROM results) as results,
    (SELECT COUNT(*) FROM domain_discoveries) as discoveries;
EOF
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}Verifying database structure...${NC}"
        echo ""
        
        # Check tables
        echo "Tables:"
        psql $DATABASE_URL -c "\dt" -t | grep -E "domains|tasks|results|domain_discoveries" | awk '{print "  ✓", $3}'
        
        echo ""
        echo "Views:"
        psql $DATABASE_URL -c "\dv" -t | awk '{print "  ✓", $3}'
        
        echo ""
        echo "Functions:"
        psql $DATABASE_URL -c "\df" -t | grep -E "set_updated_at|validate_profile_data" | awk '{print "  ✓", $3}'
        
        echo ""
        echo "Running validation:"
        psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
        
        echo ""
        echo -e "${GREEN}✓${NC} Verification complete"
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Database Statistics${NC}"
        echo ""
        
        psql $DATABASE_URL <<EOF
-- Record counts
SELECT 
    'Domains' as table_name,
    COUNT(*) as count,
    pg_size_pretty(pg_total_relation_size('domains')) as size
FROM domains
UNION ALL
SELECT 
    'Tasks',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('tasks'))
FROM tasks
UNION ALL
SELECT 
    'Results',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('results'))
FROM results
UNION ALL
SELECT 
    'Discoveries',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('domain_discoveries'))
FROM domain_discoveries;

-- Meta profiles
SELECT '' as spacer;
SELECT 'Meta Profiles:' as info;
SELECT name, array_length(profiles, 1) as profile_count 
FROM tasks 
WHERE is_meta_profile = TRUE 
ORDER BY name;
EOF
        ;;
        
    4)
        echo "Exiting."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════"
echo ""
