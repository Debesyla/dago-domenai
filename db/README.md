# Database Setup

Database initialization and management for dago-domenai.

## Quick Start

### Automated Deployment (Part of deploy.sh)

When running `./deploy.sh`, you'll be prompted for database setup:
```bash
./deploy.sh root@your-server.com /srv/dago-domenai
# Answer "y" when asked about database setup
# Provides database credentials
# ✅ Schema applied automatically
```

**What it does:**
- Tests database connection
- Applies schema.sql
- Shows basic summary

**Use when:** First-time deployment or simple schema updates

---

### Interactive Management (db/setup.sh)

For advanced database operations and local development:
```bash
cd /path/to/dago-domenai
./db/setup.sh

# Interactive menu:
# 1) Initialize fresh database (DESTRUCTIVE - drops all data)
# 2) Verify existing database
# 3) Show database statistics  
# 4) Exit
```

**What it does:**
- Full database rebuild (drops & recreates)
- Validation checks
- Detailed statistics and analysis
- Profile verification

**Use when:** 
- Local development setup
- Troubleshooting database issues
- Wanting detailed stats
- Need to rebuild from scratch

---

## Comparison: deploy.sh vs db/setup.sh

| Feature | deploy.sh | db/setup.sh |
|---------|-----------|-------------|
| **Purpose** | Automated deployment | Interactive management |
| **Location** | Remote server (via SSH) | Local or on server |
| **Prompts** | Inline credentials | Uses .env file |
| **Database ops** | Apply schema only | Full CRUD + validation |
| **Destructive** | No (safe) | Yes (option 1) |
| **Statistics** | Basic summary | Detailed analysis |
| **Best for** | First deployment | Development & troubleshooting |

**TL;DR:**
- **First deployment?** Use `deploy.sh` (answers "y" to database setup)
- **Troubleshooting?** Use `db/setup.sh` (option 2 for verification)
- **Fresh start?** Use `db/setup.sh` (option 1 to rebuild)
- **Stats?** Use `db/setup.sh` (option 3)

---

## Files

```
db/
├── schema.sql          Complete v1.0 database schema
├── setup.sh            Interactive setup script
└── README.md           This file
```

## Schema Overview

### Tables (4)
- **domains** - Domain registry with registration/active flags
- **tasks** - Task definitions with profile system support
- **results** - Analysis results with profile execution tracking
- **domain_discoveries** - Redirect/discovery tracking

### Views (5)
- **v_discovery_stats** - Discovery method statistics
- **v_top_discovery_sources** - Most productive discovery sources
- **v_profile_execution_stats** - Profile usage statistics
- **v_profile_combinations** - Common profile combinations
- **v_profile_dependency_stats** - Dependency resolution analysis

### Functions (2)
- **set_updated_at()** - Auto-update timestamps
- **validate_profile_data()** - Profile data consistency checks

### Data
- 6 meta profiles pre-populated in tasks table

## Usage

### Initialize Fresh Database
```bash
./db/setup.sh
# Choose option 1
```

**WARNING:** This drops all existing data!

### Verify Database
```bash
./db/setup.sh
# Choose option 2
```

Checks:
- All tables exist
- All views exist
- All functions exist
- Runs validation checks

### Show Statistics
```bash
./db/setup.sh
# Choose option 3
```

Shows:
- Record counts
- Table sizes
- Meta profiles

### Manual Commands

```bash
# Create schema
psql $DATABASE_URL -f db/schema.sql

# Verify
psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"

# Check tables
psql $DATABASE_URL -c "\dt"

# Check views
psql $DATABASE_URL -c "\dv"

# Check data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks WHERE is_meta_profile = TRUE;"
```

## Environment

Required environment variable in `.env`:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

## Version History

- **v1.0** - Complete schema with profile system
  - 4 tables (domains, tasks, results, domain_discoveries)
  - 5 analytics views
  - 2 functions
  - 6 meta profiles
  - Full profile system support

## Notes

- Schema is **idempotent** - safe to run multiple times
- Uses `IF NOT EXISTS` for all objects
- Uses `ON CONFLICT DO NOTHING` for data inserts
- No migrations needed - start fresh at v1.0
- For production, back up before running option 1!

## Validation

After setup, verify with:

```bash
psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
```

All checks should return **PASS**.

## Support

See main documentation:
- `docs/LOCAL_SETUP.md` - Development setup
- `docs/V10_COMPLETION.md` - Technical details
- `SCHEMA_UPDATE_REPORT.md` - Schema documentation
