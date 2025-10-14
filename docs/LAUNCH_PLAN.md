# LAUNCH_PLAN.md — Incremental Releases

This roadmap defines **sequential, non-breaking launches** for the Domain Analyzer project.  
Each launch ends in a working version, tagged in Git (e.g. `v0.3`, `v1.0`, `v2.0`, ...).  
After completing each step, commit, test, and tag before moving forward.

---

## 🟢 Version 0.1 — Project Bootstrap

### 🎯 Goal
Create the basic folder structure, environment setup, and initial documentation.  
The project should import cleanly and run without errors.

### 📋 Tasks
1. Initialize Git repository and Python virtual environment.  
2. Create `/src/` folder structure:
   - `checks/`, `core/`, `tasks/`, `utils/`, `data/`
3. Add `requirements.txt` (aiohttp, pyyaml, pytest, etc.).  
4. Add `README.md`, `DESIGN.md`, and other docs from `/docs/`.  
5. Verify VS Code + interpreter setup.

### 🧪 Validation
- `python` imports from `src/` work.  
- Folder structure matches `DESIGN.md`.

### 📦 Tag
```bash
git add .
git commit -m "v0.1 - bootstrap project"
git tag v0.1
git push origin main --tags
```

---

## 🟢 Version 0.2 — Core Utilities & Schema

### 🎯 Goal
Introduce reusable foundation: config loader, logger, and schema factory.

### 📋 Tasks
1. Add `utils/config.py` to load `config.yaml`.  
2. Add `utils/logger.py` with `setup_logger` and `safe_run_async` decorators.  
3. Add `core/schema.py` defining `new_domain_result()`.  
4. Add base `config.yaml` file.  
5. Test imports in Python shell.

### 🧪 Validation
```python
from utils.config import load_config
from utils.logger import setup_logger
from core.schema import new_domain_result
```
Should execute without errors.

### 📦 Tag
```bash
git commit -m "v0.2 - core utilities and schema"
git tag v0.2
git push origin main --tags
```

---

## 🟢 Version 0.3 — Orchestrator & Error Handling

### 🎯 Goal
Implement the orchestration layer that coordinates all checks safely.

### 📋 Tasks
1. Add `src/orchestrator.py` (uses async + safe_run decorators).  
2. Import `status_check` placeholder module.  
3. Implement simple domain loop that logs start and finish.  
4. Ensure graceful failure when domain unreachable.

### 🧪 Validation
```bash
python src/orchestrator.py domains.txt
```
Should iterate through domains and log attempts.

### 📦 Tag
```bash
git commit -m "v0.3 - orchestrator and safe_run"
git tag v0.3
git push origin main --tags
```

---

## 🟢 Version 0.4 — First Real Check (status_check)

### 🎯 Goal
Add and validate the first functional check to prove the system works end-to-end.

### 📋 Tasks
1. Implement `src/checks/status_check.py` using aiohttp.  
2. Load timeout/config from YAML.  
3. Integrate it in orchestrator.  
4. Log success/error for each domain.

### 🧪 Validation
- Running orchestrator prints `status: ok` for reachable domains.  
- Results written to console or logs.

### 📦 Tag
```bash
git commit -m "v0.4 - status_check working"
git tag v0.4
git push origin main --tags
```

---

## 🟢 Version 0.5 — Redirects, Robots, Sitemap, SSL

### 🎯 Goal
Add all remaining basic checks and verify they integrate cleanly.

### 📋 Tasks
1. Implement `redirect_check.py`, `robots_check.py`, `sitemap_check.py`, and `ssl_check.py`.  
2. Update `config.yaml` with relevant options.  
3. Test async orchestration for multiple checks.

### 🧪 Validation
- `checks` dict in result contains all modules.  
- No crashes when some URLs return 404.

### 📦 Tag
```bash
git commit -m "v0.5 - all base checks added"
git tag v0.5
git push origin main --tags
```

---

## 🟢 Version 0.6 — Database Persistence

### 🎯 Goal
Add `utils/db.py` for storing and retrieving results in SQLite (or Postgres).

### 📋 Tasks
1. Create DB tables based on `SCHEMA.md`.  
2. Add helper functions: `init_db`, `save_result`, `get_domains`.  
3. Orchestrator should persist results after each check.

### 🧪 Validation
- Database file `data/results.db` is created.  
- Query returns saved results for test domains.

### 📦 Tag
```bash
git commit -m "v0.6 - database persistence added"
git tag v0.6
git push origin main --tags
```

---

## 🟢 Version 0.7 — Reporting and Export

### 🎯 Goal
Enable output export to JSON/CSV and logging summaries.

### 📋 Tasks
1. Add `reports.py` or `export.py` module.  
2. Write JSON report to `/exports/` folder.  
3. Log summary: how many succeeded/failed.

### 🧪 Validation
- Running orchestrator produces `exports/results_<timestamp>.json`.

### 📦 Tag
```bash
git commit -m "v0.7 - reporting and export"
git tag v0.7
git push origin main --tags
```

---

## 🟢 Version 0.8 — Check Process Optimization

### 🎯 Goal
Optimize check process by implementing early bailout logic - only run expensive checks if domain is registered and active.

### 📋 Tasks
1. Update database schema:
   - Add `is_registered` (BOOLEAN) to `domains` table
   - Add `is_active` (BOOLEAN) to `domains` table
   - Run migration SQL script

2. Add placeholder checks:
   - Create `checks/whois_check.py` (placeholder for v0.8.1)
   - Create `checks/active_check.py` (placeholder for v0.8.2)

3. Update orchestrator logic:
   - Run whois check first to determine `is_registered`
   - If NOT registered → skip all other checks, save result
   - If registered → run active check to determine `is_active`
   - If NOT active → skip remaining checks, save result
   - If active → run full check suite (status, redirect, robots, sitemap, ssl)

4. Update database functions:
   - Modify `get_or_create_domain()` to handle new fields
   - Update domain flags after checks complete

### 🧪 Validation
- Unregistered domains skip all checks
- Inactive domains only run registration + active checks
- Active domains run full check suite
- Database correctly stores `is_registered` and `is_active` flags
- Significant performance improvement on domains lists with inactive/unregistered domains

### 📦 Tag
```bash
git commit -m "v0.8 - check process optimization with early bailout"
git tag v0.8
git push origin main --tags
```

---

## 🟢 Version 0.8.1 — Real WHOIS Check

### 🎯 Goal
Replace placeholder whois check with actual WHOIS lookup.

### 📋 Tasks
1. Install `python-whois` or use socket-based WHOIS queries
2. Implement real `whois_check.py`:
   - Query WHOIS servers
   - Parse registration status
   - Extract expiration date, registrar info
   - Return: `registered`, `registrar`, `expires_at`, `error`

### 🧪 Validation
- Correctly identifies registered vs unregistered domains
- Returns registrar and expiration info for registered domains

### 📦 Tag
```bash
git commit -m "v0.8.1 - real WHOIS check implementation"
git tag v0.8.1
```

---

## 🟢 Version 0.8.2 — Real Active Status Check

### 🎯 Goal
Replace placeholder active check with intelligent activity detection.

### 📋 Tasks
1. Implement real `active_check.py`:
   - Combine status check + redirect check results
   - Domain is ACTIVE if:
     - Returns 2xx status code AND doesn't redirect to different domain, OR
     - Redirects to same domain (www variant, https upgrade)
   - Domain is INACTIVE if:
     - Redirects to completely different domain
     - Returns 404, 403, 5xx errors
     - Times out or has connection errors
   - Return: `active`, `reason`, `final_domain`, `error`

### 🧪 Validation
- Correctly identifies parked domains (inactive)
- Correctly identifies redirect domains like gyvigali.lt → augalyn.lt (inactive)
- Correctly identifies working sites as active
- Correctly identifies domains with SSL issues as inactive

### 📦 Tag
```bash
git commit -m "v0.8.2 - intelligent active status detection"
git tag v0.8.2
```

---

## 🟢 Version 1.0 — Tests and Final Polish (Basic Launch)

### 🎯 Goal
Add pytest suite and prepare for continuous development.

### 📋 Tasks
1. Add `/tests/` with tests for schema, config, and checks.  
2. Add `.github/workflows/tests.yml` (optional CI).  
3. Write short developer guide in `/docs/`.

### 🧪 Validation
- `pytest` passes all tests.  
- Logs clean.

### 📦 Tag
```bash
git commit -m "v1.0 - tests and docs complete"
git tag v1.0
git push origin main --tags
```

---

# 🚀 FUTURE VERSIONS

---

## 🟣 Version 1.1 — Extended Technical Checks
- DNS resolution (A/AAAA, MX, NS).  
- IP/ASN lookup → hosting provider info.  
- SSL certificate analysis (issuer, expiry, subject).  
- HTTP headers snapshot (server type, technologies).  
- Basic tech detection (Wappalyzer-style).

---

## 🟣 Version 1.2 — Content & Structure Insights
- Crawl sitemap and robots.txt for structure info.  
- Language detection from HTML `<html lang>` or content.  
- Extract meta tags and titles.  
- Detect social links and email addresses.

---

## 🟣 Version 1.3 — Business & Ownership Context
- WHOIS/RDAP lookup for registrant, registrar, expiry date.  
- Cross-check with public company registry by name or email.  
- Domain age, registrar reputation, and hosting geolocation.  
- Reverse WHOIS (same org owning multiple domains).

---

## 🟣 Version 2.0 — AI-Assisted Domain Intelligence

### 🎯 Goal
Introduce AI and LLM-based classifiers for deeper content understanding.

- Use LLM to read homepage content → classify domain type:  
  *E-shop, company page, blog, parked, expired, spammy, etc.*  
- Summarize what the site promotes or represents.  
- Detect product/service categories (via NLP embeddings).  
- Cluster similar domains by topic or brand.

---

## 🟣 Version 2.1 — Enrichment and Scoring
- Integrate external APIs (Ahrefs, SimilarWeb, SEMrush) for:  
  - Traffic & backlinks  
  - Domain authority  
  - Reputation & blacklist data  
- Combine all checks into a “domain quality score.”

---

## 🟣 Version 3.0 — Frontend Dashboard

### 🎯 Goal
Provide a visual web interface to explore analyzed domains.

- Web dashboard (FastAPI + React or similar).  
- Search, filter, and sort domains.  
- Charts for domain categories, hosts, CMS usage, etc.  
- Export UI for reports.  
- (Optional) Authentication for private datasets.

---

## 🟣 Later Ideas
- Distributed async processing cluster.  
- Continuous monitoring mode (scheduled rechecks).  
- Domain suggestion engine (find similar or free names).  
- Integration with company registry APIs.  
- AI summaries: “Describe this domain in one sentence.”

---

**Usage summary:**  
After completing each version, commit, tag, and push manually.  
Each version must *run and not break existing functionality* before moving on.
