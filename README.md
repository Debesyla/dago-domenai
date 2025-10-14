# Domain Analyzer

A modular, async-first backend for analyzing websites and domains — running multiple independent checks (status, redirects, robots.txt, sitemap, SSL, DNS) and storing structured JSON results in PostgreSQL.

## Version 0.6 — Database Persistence ✅

### What's New in v0.6
- ✅ **Database Module** (`src/utils/db.py`)
  - PostgreSQL connection with context managers
  - Automatic domain and task creation
  - Result persistence after each scan
  - Query functions for retrieving historical data
  
- ✅ **Orchestrator Integration**
  - Automatic saving to database after each domain scan
  - Configurable persistence (can be disabled)
  - Graceful handling of database errors
  
- ✅ **Query Utilities**
  - `test_db.py` - Database connection testing
  - `query_db.py` - CLI tool for querying results
    - `stats` - Database statistics
    - `domains` - List all domains
    - `latest` - Show recent results
    - `domain <name>` - Show details for specific domain
  
- ✅ **Database Functions**
  - `init_db()` - Verify database connection
  - `save_result()` - Persist domain analysis
  - `get_domains()` - List all domains
  - `get_domain_results()` - Get history for domain
  - `get_latest_results()` - Recent results across all domains
  - `get_stats()` - Database statistics

### Database Schema

The system uses three main tables:
- **domains** - Tracked domains with timestamps
- **tasks** - Task definitions (e.g., 'basic-scan')
- **results** - Analysis results stored as JSONB

### Usage

```bash
# Run analysis (automatically saves to database)
python -m src.orchestrator domains.txt

# Query database statistics
python query_db.py stats

# List all domains
python query_db.py domains

# Show latest results
python query_db.py latest

# Show details for specific domain
python query_db.py domain gyvigali.lt

# Test database connection
python test_db.py
```

### Example Query Output

```
📊 Database Statistics:
  Total Domains: 6
  Total Results: 10
  Results by Status:
    - success: 9
    - partial: 1

🔍 Results for: gyvigali.lt
  Grade: A
  HTTPS: True
  Reachable: True
  Checks:
    - status: 200 (211ms)
    - redirects: 1 redirects
    - ssl: Let's Encrypt, expires in 48 days
    - robots: ✅
    - sitemap: ✅
```

### Files Added/Modified in v0.6
- `src/utils/db.py` — Database module with connection pooling
- `src/orchestrator.py` — Integrated database persistence
- `config.yaml` — Added `save_results` flag
- `test_db.py` — Database testing utility
- `query_db.py` — Database query CLI tool

---

## Version History

### Version 0.5 — All Base Checks ✅

### What's New in v0.5
- ✅ **Redirect Check** (`src/checks/redirect_check.py`)
  - Follows redirect chain up to max_hops
  - Returns: chain, length, final_url
  - Detects 301, 302, 303, 307, 308 redirects
  
- ✅ **Robots.txt Check** (`src/checks/robots_check.py`)
  - Fetches and parses robots.txt
  - Returns: found, allow, disallow, valid
  - Lists all Allow/Disallow rules
  
- ✅ **Sitemap Check** (`src/checks/sitemap_check.py`)
  - Searches for sitemap.xml in common locations
  - Returns: found, url, count_urls, valid
  - Counts URL entries in sitemap
  
- ✅ **SSL Certificate Check** (`src/checks/ssl_check.py`)
  - Validates SSL certificate
  - Returns: valid, issuer, days_until_expiry, expires_at
  - Detects certificate issues and expiration

- ✅ **Enhanced Configuration** (`config.yaml`)
  - Added settings for all checks
  - Configurable max_hops for redirects
  - Enable/disable individual checks

### Current Features

**Complete Check Results:**
```json
{
  "domain": "gyvigali.lt",
  "meta": {
    "timestamp": "2025-10-14T12:19:20.985532+00:00",
    "task": "basic-scan",
    "execution_time_sec": 1.42,
    "status": "success"
  },
  "checks": {
    "status": {
      "code": 200,
      "ok": true,
      "final_url": "https://augalyn.lt/?utm_source=gyvigali",
      "duration_ms": 408
    },
    "redirects": {
      "chain": ["https://gyvigali.lt", "https://augalyn.lt/?utm_source=gyvigali"],
      "length": 1,
      "final_url": "https://augalyn.lt/?utm_source=gyvigali"
    },
    "robots": {
      "found": true,
      "allow": ["/wp-admin/admin-ajax.php"],
      "disallow": ["/wp-admin/", ...],
      "valid": true
    },
    "sitemap": {
      "found": true,
      "url": "https://gyvigali.lt/sitemap.xml",
      "count_urls": 9,
      "valid": true
    },
    "ssl": {
      "valid": true,
      "issuer": "Let's Encrypt",
      "days_until_expiry": 49,
      "expires_at": "2025-12-02T13:00:02+00:00"
    }
  },
  "summary": {
    "reachable": true,
    "https": true,
    "grade": "A"
  }
}
```

### Usage

```bash
# Analyze multiple domains from file
python -m src.orchestrator domains.txt

# Analyze a single domain
python -m src.orchestrator --domain example.com

# Test specific domain with JSON output
python test_v05.py gyvigali.lt
```

### Files Added/Modified in v0.5
- `src/checks/redirect_check.py` — Redirect chain tracking
- `src/checks/robots_check.py` — Robots.txt parser
- `src/checks/sitemap_check.py` — Sitemap.xml finder
- `src/checks/ssl_check.py` — SSL certificate validator
- `src/orchestrator.py` — Integrated all checks with enable/disable
- `config.yaml` — Added configuration for all checks
- `domains.txt` — Added gyvigali.lt and debesyla.lt test domains

---

## Version History

### Version 0.4 — First Real Check (HTTP Status) ✅

### What's Done
- ✅ Git repository initialized
- ✅ Python virtual environment created (`.venv`)
- ✅ Basic folder structure created:
  - `src/checks/` — Domain check modules (empty, ready for v0.2+)
  - `src/core/` — Schema and parsers (empty, ready for v0.2+)
  - `src/utils/` — Config, logger, db (empty, ready for v0.2+)
  - `src/tasks/` — Task orchestration (empty, ready for v0.3+)
  - `src/data/` — SQLite DB and exports
- ✅ All folders have `__init__.py` for proper imports
- ✅ Dependencies updated in `requirements.app.txt`
- ✅ Documentation from docs/ folder
- ✅ Old implementation archived in `archive/`

### Project Structure (v0.1)

```
/Users/dan/Documents/IT/dago/dago-cloud/dago-domenai/
├── src/
│   ├── __init__.py
│   ├── checks/
│   │   └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   ├── tasks/
│   │   └── __init__.py
│   └── data/
│       └── .gitkeep
├── db/                  # SQL schema files (Postgres)
│   ├── schema.sql
│   └── seed.sql
├── docs/                # Design docs and plans
│   ├── CONTEXT.md
│   ├── LAUNCH_PLAN.md
│   ├── LOCAL_SETUP.md
│   ├── PLAN.md
│   ├── PROJECT_DOCS.md
│   └── README.md
├── archive/             # Old implementation (for reference)
│   ├── config.py
│   └── db_test_insert.py
├── requirements.app.txt # Python dependencies
├── .env.example         # Example environment file
├── .env                 # Local environment (DB connection)
└── README.md           # This file
```

### Validation

You can verify the structure is ready:

```bash
# Activate venv
source .venv/bin/activate

# Test imports work
python -c "from src.checks import *; from src.core import *; from src.utils import *; print('✅ All imports working')"
```

### Dependencies Installed

- `psycopg2-binary` — PostgreSQL adapter
- `python-dotenv` — Environment config
- `pyyaml` — YAML config (for v0.2)
- `aiohttp` — Async HTTP (for v0.2)
- `requests` — Sync HTTP fallback
- `rich` — CLI output
- `pytest` — Testing (for v1.0)
- `pytest-asyncio` — Async testing

### Local Database (Optional)

Your local Postgres setup from before still works:

```bash
source .env
psql "$DATABASE_URL" -f db/schema.sql
psql "$DATABASE_URL" -f db/seed.sql
```

See `docs/LOCAL_SETUP.md` for full macOS setup instructions.

### What's Next

Following **LAUNCH_PLAN.md** incrementally:

**v0.6 — Database Persistence**
- Implement `utils/db.py` for PostgreSQL operations
- Save domain analysis results to database
- Query and retrieve historical data
- Add connection pooling

**v0.7+ — Advanced Features**
- Reporting and exports (JSON, CSV)
- Comprehensive unit testing
- AI-powered insights and recommendations
- Web dashboard interface
- API endpoints

### Documentation

- `docs/PROJECT_DOCS.md` — Full design and schema docs
- `docs/LAUNCH_PLAN.md` — Incremental release plan (follow this!)
- `docs/LOCAL_SETUP.md` — macOS local dev setup
- `docs/PLAN.md` — Original project plan

---

**Status:** v0.5 complete — All base checks implemented! 🚀

