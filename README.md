# Domain Analyzer

A modular, async-first backend for analyzing websites and domains — running multiple independent checks (status, redirects, robots.txt, sitemap, SSL, DNS) and storing structured JSON results.

## Version 0.1 — Project Bootstrap ✅

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

**v0.2 — Core Utilities & Schema**
- Add `utils/config.py` (YAML loader)
- Add `utils/logger.py` (logging + safe_run decorators)
- Add `core/schema.py` (result factory)
- Add `config.yaml` file
- Test: All modules import without errors

**v0.3 — Orchestrator**
- Add `src/orchestrator.py` (async coordination)
- Test: Can run with placeholder checks

**v0.4 — First Real Check**
- Add `checks/status_check.py`
- Test: Status check returns real results

### Documentation

- `docs/PROJECT_DOCS.md` — Full design and schema docs
- `docs/LAUNCH_PLAN.md` — Incremental release plan (follow this!)
- `docs/LOCAL_SETUP.md` — macOS local dev setup
- `docs/PLAN.md` — Original project plan

---

**Status:** v0.1 complete — project bootstrapped and ready for incremental development 🎯

