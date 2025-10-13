# DESIGN.md

## Design — Domain Analyzer

### Purpose
A modular backend to analyze domains — running multiple independent website checks (status, redirects, robots.txt, sitemap, SSL, DNS, WHOIS) — storing structured results for later use in analytics, dashboards, or API endpoints.

### Goals
- **Modular and extendable**: Each check is a separate file with a shared schema.
- **Data-first design**: All results conform to a standard JSON schema.
- **Async-first execution**: Parallel scans for multiple domains.
- **Environment-aware**: Runs locally or on VPS with SQLite/Postgres.

### Architecture Overview
```
/srv/dago-domenai/
├── src/
│   ├── checks/          # One file per check
│   ├── tasks/           # Orchestration runners
│   ├── core/            # Schema, http_utils, parsers
│   ├── utils/           # Logger, config, db
│   └── data/            # Local exports, SQLite DB
├── config.yaml
└── tests/
```

### Core Flow
1. **Input**: domain list or DB table.
2. **Orchestration**: decide which checks to run per config.
3. **Execution**: run checks asynchronously.
4. **Persistence**: save results (DB/JSON).
5. **Reporting**: optional export for analytics.

### Non-functional Requirements
- Logs all activity (file + console).
- Handles retries, timeouts, and graceful failures.
- Easy to test and debug.
- Ready for CLI and API expansion.

---

# SCHEMA.md

## JSON Result Schema (v1.0)
Each domain scan outputs a unified JSON structure shared by all checks.

```json
{
  "domain": "example.com",
  "meta": {
    "timestamp": "2025-10-13T20:00:00Z",
    "task": "basic_scan",
    "execution_time_sec": 4.12,
    "status": "success",
    "errors": [],
    "schema_version": "1.0"
  },
  "checks": {
    "status": {...},
    "redirects": {...},
    "robots": {...},
    "sitemap": {...},
    "ssl": {...}
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

Each `check` returns its own dict and gets merged into `checks.<check_name>`.

### Database Schema (SQLite/Postgres)

**domains** — list of tracked domains
```
id INTEGER PK
 domain TEXT UNIQUE
 status TEXT
 created_at TIMESTAMP
 last_checked TIMESTAMP
 notes TEXT
```

**checks** — metadata about available checks
```
id INTEGER PK
 name TEXT UNIQUE
 description TEXT
 enabled BOOLEAN
```

**results** — individual check results per domain
```
id INTEGER PK
 domain_id INTEGER (FK → domains.id)
 check_id INTEGER (FK → checks.id)
 status TEXT
 message TEXT
 data JSONB
 duration_ms INTEGER
 created_at TIMESTAMP
```

(optional) **runs** — group full scan sessions
```
id INTEGER PK
 started_at TIMESTAMP
 finished_at TIMESTAMP
 domains_count INTEGER
```

---

# CONFIG.md

## config.yaml
Configuration file controlling runtime, database, and checks.

```yaml
env: development
debug: true

database:
  engine: sqlite
  sqlite_path: ./src/data/results.db
  postgres_url: postgresql://user:password@localhost:5432/domains

logging:
  level: INFO
  log_dir: ./logs
  max_size_mb: 5
  backup_count: 5

orchestrator:
  concurrency: 5
  retries: 2
  delay: 1.0
  timeout: 10
  save_to_db: true
  export_results: true
  export_dir: ./exports

network:
  user_agent: DomainAnalyzerBot/1.0
  request_timeout: 5
  follow_redirects: true
  verify_ssl: true

checks:
  status:
    enabled: true
    expected_statuses: [200, 301, 302]
  redirect:
    enabled: true
    max_hops: 10
  robots:
    enabled: true
  sitemap:
    enabled: true
  ssl:
    enabled: true

scheduler:
  enabled: false
  cron: "0 6 * * *"
  max_domains_per_run: 100
```

---

# ORCHESTRATION.md

## Flow Diagram
```
main.py → tasks/basic_scan.py → checks/* → db.py → exports → logs
```

### Detailed Flow
1. CLI or scheduler triggers orchestrator.
2. Orchestrator loads domains (from file or DB).
3. For each domain:
   - Create `DomainResult` via `core/schema.new_domain_result()`
   - Execute each enabled check asynchronously.
   - Collect and merge results.
   - Update summary and timing.
   - Save results via `utils/db.save_result()`
4. After run completion:
   - Export all domain results (JSON)
   - Update `runs` table (optional)
   - Log summary (success/fail count)

### CLI Usage Examples
```
python -m src.orchestrator domains.txt
python -m src.orchestrator --file domains.txt --output results.json
python -m src.orchestrator --domain example.com
```

---

# TASKS.md

## Implementation Roadmap

### Phase 1 — Core Modules
1. Create folder structure with `__init__.py` files.
2. Implement:
   - `core/schema.py` (factory for result)
   - `utils/config.py` (YAML loader)
   - `utils/logger.py` (logging + safe_run)
3. Scaffold and test `src/orchestrator.py`.

### Phase 2 — Check Modules
Each check returns dict → merged into `DomainResult['checks']`.

#### status_check.py
- GET http(s)://domain
- Return `{code, ok, final_url, duration_ms, error}`

#### redirect_check.py
- Follow redirects up to `max_hops`
- Return `{chain, length, final_url, error}`

#### robots_check.py
- GET `/robots.txt`
- Parse rules, return `{found, allow, disallow, valid, error}`

#### sitemap_check.py
- Locate `/sitemap.xml`
- Parse, count URLs, return `{found, url, count_urls, valid, error}`

#### ssl_check.py
- Check certificate issuer and expiry days.

### Phase 3 — Persistence
- Implement `utils/db.py` with SQLite/PG adapter.
- Add `save_result(domain, check_name, data, duration_ms)`.

### Phase 4 — Testing
- Unit tests in `/tests/` using pytest.
- Mock network responses.
- Add `make test` and CI workflow.

---

# SETUP.md

## Local Setup

1. Clone repo and `cd` into it.
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example → .env`
5. Edit DB URL in `.env` if using Postgres.
6. `python src/orchestrator.py domains.txt`

## VS Code Integration
- Open project folder in VS Code.
- Use Copilot and this design doc to generate modules step-by-step.
- Use built-in terminal for commands.
- Add Python extension for linting & debugging.

---

# COPILOT_PROMPTS.md

### Prompt — Implement status_check
```
Implement async Python module `src/checks/status_check.py`.
Use aiohttp, `safe_run_async`, and return dict with code, ok, final_url, error.
Read config values for timeout and expected_statuses.
```

### Prompt — Implement db helper
```
Implement `src/utils/db.py` with init_db, get_domains, save_result.
Use SQLite first; support Postgres via URL later.
```

### Prompt — Implement orchestrator
```
Implement orchestrator that loads domains, runs enabled checks concurrently, merges results, saves them, and logs summary.
```

---

# IMPLEMENTATION_STEPS.md

1. **Initialize structure** — create `/src/` with subfolders and `__init__.py`.
2. **Schema** — add `core/schema.py`.
3. **Config & Logging** — add `utils/config.py` and `utils/logger.py`.
4. **Checks** — implement each under `/checks/`.
5. **DB layer** — implement `utils/db.py`.
6. **Orchestrator** — wire everything in `src/orchestrator.py`.
7. **Testing** — add pytest tests.
8. **Docs** — copy all .md files to `/docs/`.
9. **Run** — `python src/orchestrator.py domains.txt`.

---

These markdown files now form a complete set of development and design docs for VS Code or Copilot.

