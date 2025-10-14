# Domain Analyzer

A modular, async-first backend for analyzing websites and domains — running multiple independent checks (status, redirects, robots.txt, sitemap, SSL, DNS) and storing structured JSON results.

## Version 0.4 — First Real Check (HTTP Status) ✅

### What's New in v0.4
- ✅ **HTTP Status Check** (`src/checks/status_check.py`)
  - Fetches HTTP status code using aiohttp
  - Returns: code, ok, final_url, duration_ms
  - Handles timeouts and connection errors gracefully
- ✅ **Orchestrator Integration**
  - Calls status_check for each domain
  - Tracks execution time and error handling
  - Updates result metadata and summary
- ✅ **Enhanced Error Handling**
  - SSL/certificate errors detected
  - Connection errors reported
  - Graceful degradation on failures

### Current Features

**Status Check Results:**
```json
{
  "domain": "example.com",
  "meta": {
    "timestamp": "2025-10-14T12:04:15.649537+00:00",
    "task": "basic-scan",
    "execution_time_sec": 0.5,
    "status": "success",
    "schema_version": "1.0"
  },
  "checks": {
    "status": {
      "code": 200,
      "ok": true,
      "final_url": "https://example.com",
      "duration_ms": 503
    }
  },
  "summary": {
    "reachable": true,
    "https": true,
    "issues": 0,
    "warnings": 0,
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
```

### Files Added/Modified in v0.4
- `src/checks/status_check.py` — HTTP status check with aiohttp
- `src/orchestrator.py` — Updated to integrate status_check
- `src/core/schema.py` — Fixed None handling for failed checks

---

## Version History

### Version 0.3 — Orchestrator ✅

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

**v0.5 — Additional Checks**
- Add redirect check (follow chain)
- Add robots.txt check
- Add sitemap.xml check
- Add SSL/TLS certificate check
- Test: All checks return structured data

**v0.6 — Database Persistence**
- Save results to PostgreSQL
- Query and retrieve historical data

**v0.7+ — Advanced Features**
- Reporting and exports
- Comprehensive testing
- AI-powered insights
- Dashboard interface

### Documentation

- `docs/PROJECT_DOCS.md` — Full design and schema docs
- `docs/LAUNCH_PLAN.md` — Incremental release plan (follow this!)
- `docs/LOCAL_SETUP.md` — macOS local dev setup
- `docs/PLAN.md` — Original project plan

---

**Status:** v0.4 complete — HTTP status check working! 🚀

