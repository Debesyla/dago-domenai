# Database Setup

Simple database initialization for dago-domenai v1.0.

## Quick Start

### First Time Setup

```bash
cd db
./setup.sh
# Choose option 1 to initialize fresh database
```

### Manual Setup

```bash
# Option 1: Using script
./db/setup.sh

# Option 2: Direct SQL
psql $DATABASE_URL -f db/schema.sql
```

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
- **discovery_stats** - Discovery method statistics
- **top_discovery_sources** - Most productive discovery sources
- **profile_execution_stats** - Profile usage statistics
- **profile_combinations** - Common profile combinations
- **profile_dependency_stats** - Dependency resolution analysis

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
