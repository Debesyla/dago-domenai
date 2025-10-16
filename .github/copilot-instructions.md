# Copilot Instructions for DAGO Domain Analyzer

## Project Architecture

**DAGO** is an async domain analysis tool with a **composable profile system** organized by data source (DNS, HTTP, SSL, WHOIS) rather than scan depth. This enables efficient data reuse and flexible combinations.

### Core Concepts

1. **Profile System** (`src/profiles/`): The heart of the application
   - Profiles are organized by **data source**, not scan depth (e.g., `dns`, `ssl`, `whois` vs traditional "basic scan", "full scan")
   - Meta profiles (e.g., `quick-check`, `standard`, `complete`) expand to multiple core profiles
   - Automatic dependency resolution via topological sorting in `profile_loader.py`
   - All profiles defined in `profile_schema.py` with `PROFILE_DEPENDENCIES` and `PROFILE_METADATA`

2. **Orchestrator** (`src/orchestrator.py`): Main execution engine
   - Implements **early bailout optimization**: runs WHOIS first, skips unregistered domains
   - Profile-aware check selection in `determine_checks_to_run()` with legacy fallback
   - Async domain processing with configurable concurrency

3. **Check Modules** (`src/checks/`): All checks follow `async def run_*_check(domain: str, config: Dict) -> Dict` pattern
   - Each returns structured dict with check-specific data
   - No classes, just async functions for simplicity

4. **Result Schema** (`src/core/schema.py`): Standardized JSON structure
   - Every result has `meta`, `checks`, and `summary` sections
   - Use factory functions: `new_domain_result()`, `add_check_result()`, `update_summary()`

5. **Database Layer** (`src/utils/db.py`): PostgreSQL with JSONB
   - Context manager pattern: `DatabaseConnection(db_url)` for automatic commit/rollback
   - Schema in `db/schema.sql` includes domain flags (`is_registered`, `is_active`) for early bailout
   - Profile tracking: `profiles_requested`, `profiles_executed`, `execution_plan` columns

## Key Workflows

### Running Analysis
```bash
# Profile-based execution (preferred v1.0+ method)
python -m src.orchestrator domains.txt --profiles quick-check
python -m src.orchestrator domains.txt --profiles dns,ssl,seo
python -m src.orchestrator --domain example.com --profiles complete

# Export results
# Exports automatically go to ./exports/ as JSON and/or CSV based on config.yaml
```

### Testing
```bash
# Run all tests (43 unit tests, 100% passing as of v1.0)
pytest

# Run specific test categories
pytest tests/unit/test_profiles.py -v     # Profile system (84 assertions)
pytest tests/integration/                 # End-to-end tests
pytest --cov=src --cov-report=html        # With coverage
```

### Database Setup
```bash
# Interactive setup script (creates DB, runs schema, verifies)
./db/setup.sh

# Manual verification
psql $DATABASE_URL -f db/schema.sql
```

## Project-Specific Conventions

### Profile System Design Pattern
- **Core profiles** (`whois`, `dns`, `http`, `ssl`): Make external API calls, no dependencies
- **Analysis profiles** (`headers`, `content`, `seo`): Process data from core profiles, have dependencies
- **Intelligence profiles** (`security`, `compliance`, `business`): Complex dependencies, business insights
- **Meta profiles** (`quick-check`, `standard`, `complete`): Expand to other profiles

When adding a new profile:
1. Define in `profile_schema.py` under `PROFILE_DEPENDENCIES` and `PROFILE_METADATA`
2. Add to `ProfileType` enum
3. Update `config.yaml` with checks configuration
4. Create or update check module in `src/checks/`
5. Add tests in `tests/unit/test_profiles.py`

### Error Handling Pattern
Checks return partial results on error rather than raising exceptions:
```python
async def run_check(domain: str, config: Dict) -> Dict:
    try:
        # ... check logic
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e), "data": None}
```

### Configuration Access
- `config.yaml` is the single source of truth
- Load via `src.utils.config.load_config()`
- Database URL from `DATABASE_URL` env var or `config['database']['postgres_url']`
- Check-specific config: `config['checks']['whois']['enabled']`

### Async Patterns
- All check functions are `async def`
- Orchestrator uses `asyncio.gather()` for parallel execution
- aiohttp for HTTP requests with configurable timeout (`config['network']['request_timeout']`)

## Version History Context

- **v0.8**: Introduced early bailout optimization (WHOIS first, skip unregistered)
- **v0.9**: Added domain discovery tracking (redirects create `domain_discoveries` records)
- **v0.10**: Complete profile system with dependency resolution
- **v1.0**: Production release with test suite and streamlined DB setup
- **v1.1** (current): Dual protocol WHOIS (DAS + port 43) with complete registration data

## Common Tasks

### Adding a New Check
1. Create `src/checks/your_check.py` with `async def run_your_check(domain, config) -> dict`
2. Import in `src/orchestrator.py`
3. Add to profile in `config.yaml` and `profile_schema.py`
4. Update orchestrator's check mapping in `determine_checks_to_run()` or `process_domain()`
5. Add result to schema in `src/core/schema.py` if needed
6. Write tests in `tests/unit/` and `tests/integration/`

### Working with Database
- Use `DatabaseConnection` context manager (never manual commit/rollback)
- Results stored as JSONB in `results.data` column
- Domain flags (`is_registered`, `is_active`) indexed for fast filtering
- Use `get_or_create_domain()` to ensure domain exists before saving results

### Export Customization
- `ResultExporter` class in `src/utils/export.py`
- Supports JSON, CSV, and summary statistics
- CSV uses `checks_to_columns()` to flatten JSONB into columns
- Export config in `config.yaml` under `export` section

## Important Files to Know

- `src/profiles/profile_schema.py`: Profile definitions and dependencies (the "schema of record")
- `src/profiles/profile_loader.py`: Topological sort and resolution logic
- `src/orchestrator.py`: Main execution flow with early bailout
- `config.yaml`: All configuration including profile check mappings
- `db/schema.sql`: Complete database schema (consolidated, no migrations)
- `docs/TASK_PROFILES.md`: User-facing profile documentation (keep in sync with schema)

## Lithuanian Domain (.lt) Specifics

WHOIS checks use **dual protocol approach** (v1.1):

### DAS Protocol (Domain Availability Service)
- **Purpose**: Fast bulk registration status checking
- **Server**: `das.domreg.lt:4343` (configured in `config.yaml`)
- **Rate limit**: 4 queries/second (Lithuanian registry supports "several dozens/sec")
- **Protocol**: Socket-based, not HTTP
- **Returns**: Domain name + status only (registered/available)
- **Used for**: Early bailout optimization (skip unregistered domains)

### Standard WHOIS (Port 43)
- **Purpose**: Detailed registration data for registered domains only
- **Server**: `whois.domreg.lt:43`
- **Rate limit**: 100 queries per 30 minutes (STRICT - IP blocking enforced)
- **Returns**: Complete data (registrar, dates, nameservers, contacts)
- **Rate limiter**: Token bucket implementation in `WHOISClient` class
- **Graceful degradation**: Returns DAS-only data if rate limited

### Implementation
```python
# Dual protocol flow in run_whois_check():
1. DAS check (fast) → Is registered?
   - If NO → Return 'available' (early bailout, 0.02s)
   - If YES → Continue to step 2

2. WHOIS query (detailed) → Get full data
   - If rate limited → Return DAS data only
   - If success → Return complete JSONB structure (0.10s)
```

See `src/checks/whois_check.py` for implementation details.
