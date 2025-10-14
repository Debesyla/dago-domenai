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

## 🟢 Version 0.9 — Smart Redirect Capture

### 🎯 Goal
Automatically discover and add new Lithuanian domains when they appear as redirect targets, intelligently growing the domain database.

### 📋 Tasks
1. Implement redirect capture logic:
   - After redirect check completes, analyze `final_url`
   - If domain redirected to different .lt domain → capture it
   - Extract main domain (handle subdomains intelligently)
   - Check if new domain already exists in database
   - If not → add to database for future scanning

2. Smart subdomain handling:
   - **Keep subdomains** for: `.gov.lt`, `.lrv.lt` (government sites)
     - Example: `stat.gov.lt` ≠ `strata.gov.lt` (both important)
   - **Strip subdomains** for other TLDs:
     - `ideas.dago.lt` → add only `dago.lt`
     - `www.example.lt` → add only `example.lt`
   - Configurable whitelist for other special cases

3. Domain extraction utility:
   - Create `utils/domain_utils.py`
   - Function: `extract_main_domain(url, keep_subdomain_patterns)`
   - Function: `is_lithuanian_domain(domain)`
   - Function: `should_capture_domain(source_domain, target_domain)`

4. Configuration:
   - Add to `config.yaml`:
     ```yaml
     redirect_capture:
       enabled: true
       target_tlds: ['.lt']  # Only capture Lithuanian domains
       keep_subdomains_for: ['.gov.lt', '.lrv.lt']
       ignore_common_services: ['google.lt', 'facebook.com', 'youtube.com']
     ```

5. Database function:
   - Add `add_discovered_domain(domain, discovered_from, discovery_reason)`
   - Track where domain was discovered from for analytics

### 🧪 Validation
- `gyvigali.lt` → `augalyn.lt` redirect adds `augalyn.lt` to database
- `ideas.dago.lt` → extracts and adds only `dago.lt`
- `stat.gov.lt` → keeps full domain (government exception)
- Domains already in database are not duplicated
- Discovery tracking shows which domains led to new discoveries

### 📊 Expected Impact
With 1000 domains analyzed:
- ~10-20% redirect to other .lt domains
- Could discover 100-200 new domains automatically
- Creates organic database growth through network effect

### 📦 Tag
```bash
git commit -m "v0.9 - smart redirect capture for domain discovery"
git tag v0.9
git push origin main --tags
```

---

## 🟢 Version 0.10 — Composable Profile System

### 🎯 Goal
Restructure the task system to use **composable, data-source-based profiles** instead of rigid scan tiers. Enable users to mix and match profiles for custom analysis strategies.

### 📋 Problem Statement
Current state:
- Task names are generic (`check_status` vs `basic-scan`)
- Inefficient: `full-scan` re-queries same data sources as `basic-scan`
- Not flexible: Can't get "just DNS data" or "just SSL info"
- Adding new checks requires restructuring all task definitions

### 🎯 Solution: Composable Profiles Organized by Data Source
Organize profiles by what they query, not by scan depth:
- **Core Data Profiles**: Make external API calls (`whois`, `dns`, `http`, `ssl`)
- **Analysis Profiles**: Process core data without additional calls (`headers`, `content`, `infrastructure`)
- **Intelligence Profiles**: Business insights (`security`, `business`, `language`, `clustering`)
- **Meta Profiles**: Pre-configured combinations (`quick-check`, `standard`, `complete`)

**Key Innovation**: One DNS query returns A, AAAA, MX, NS, TXT records together. Users combine profiles as needed.

### 📋 Tasks

#### 1. Review Composable Profile Matrix
**Reference:** See `docs/TASK_MATRIX.md` for complete profile definitions.

The system now has **22 profiles** in 4 categories:

**🔵 Core Data (4 profiles):**
- `whois` - Registration data (1 API call)
- `dns` - All DNS records (1 query set)
- `http` - Connectivity and redirects (1-2 requests)
- `ssl` - Certificate analysis (1 handshake)

**🟢 Analysis (5 profiles):**
- `headers` - HTTP headers (depends on `http`)
- `content` - On-page content (depends on `http`)
- `infrastructure` - Hosting analysis (depends on `dns`, `http`)
- `technology` - Tech stack detection (depends on `http`, `content`)
- `seo` - SEO checks (depends on `http`, `content`)

**🟡 Intelligence (7 profiles):**
- `security` - Vulnerability scans
- `compliance` - GDPR, privacy
- `business` - Company info
- `language` - Language detection
- `fingerprinting` - Visual analysis
- `clustering` - Portfolio detection

**🟠 Meta (6 profiles):**
- `quick-check` - Fast filtering
- `standard` - General analysis
- `technical-audit` - Security focus
- `business-research` - Market intelligence
- `complete` - Everything
- `monitor` - Change tracking

#### 2. Create Migration Script
- File: `db/migrations/v0.10_composable_profiles.sql`
- Clean existing task-based data
- Document new profile system

```sql
-- Clear old task-based system
DELETE FROM results WHERE TRUE;  -- Fresh start with new system
DELETE FROM tasks;

-- Note: Profiles are now defined in config.yaml, not in database
-- The tasks table can be repurposed or removed in future versions

-- Reset domains for re-scanning with new profile system
UPDATE domains SET updated_at = NULL, is_registered = NULL, is_active = NULL;
```

#### 3. Update Result Schema
Enhance metadata to track which profiles were used:

```json
{
  "domain": "example.com",
  "meta": {
    "timestamp": "2025-10-14T12:00:00Z",
    "profiles": ["dns", "ssl", "http"],
    "checks_performed": ["dns_a_record", "dns_mx_records", "ssl_expiration", "http_status"],
    "dependencies_resolved": {
      "dns": "completed",
      "ssl": "completed",
      "http": "completed"
    },
    "execution_time_sec": 2.8,
    "status": "success",
    "schema_version": "2.0"
  },
  "profiles": {
    "dns": {
      "a_records": ["93.184.216.34"],
      "mx_records": [...],
      "txt_records": [...]
    },
    "ssl": {
      "expiration_date": "2026-03-01",
      "issuer": "DigiCert"
    },
    "http": {
      "status_code": 200,
      "redirect_chain": []
    }
  }
}
```

#### 4. Update Orchestrator
Implement profile composition logic:

```python
# Pseudocode for v0.10 orchestrator

class ProfileOrchestrator:
    def __init__(self, config):
        self.profile_definitions = config['profiles']
        self.meta_profiles = config['meta_profiles']
        
    def resolve_profiles(self, requested_profiles: List[str]) -> Dict:
        """Resolve profile dependencies and execution order"""
        resolved = {}
        
        # Expand meta profiles
        expanded = self.expand_meta_profiles(requested_profiles)
        
        # Build dependency graph
        for profile in expanded:
            deps = self.profile_definitions[profile].get('depends_on', [])
            resolved[profile] = {
                'dependencies': deps,
                'checks': self.profile_definitions[profile]['checks']
            }
        
        # Topological sort for execution order
        execution_order = self.topological_sort(resolved)
        return execution_order
    
    async def process_domain(self, domain: str, profiles: List[str]):
        """Run checks for requested profiles"""
        execution_plan = self.resolve_profiles(profiles)
        results = {'profiles': {}}
        
        # Run profiles in dependency order
        for profile in execution_plan:
            profile_result = await self.run_profile(domain, profile, results)
            results['profiles'][profile] = profile_result
        
        # Record metadata
        results['meta'] = {
            'profiles': profiles,
            'checks_performed': self.extract_checks(results),
            'execution_time_sec': ...,
        }
        
        return results
```

#### 5. Create Profile Configuration
Define all profiles in `config.yaml`:

```yaml
# Core Data Profiles
profiles:
  whois:
    description: "Registration and ownership information"
    depends_on: []
    checks:
      - whois_registration_status
      - registrar_name
      - registration_date
      - expiration_date
      - registrant_org
      - privacy_protection
      - domain_age
  
  dns:
    description: "DNS resolution and records"
    depends_on: []
    checks:
      - dns_a_record
      - dns_aaaa_record
      - dns_mx_records
      - dns_txt_records
      - dns_ns_records
      - dns_cname
  
  http:
    description: "HTTP connectivity and behavior"
    depends_on: []
    checks:
      - http_status
      - redirect_chain
      - response_time
      - https_available
  
  ssl:
    description: "SSL/TLS certificate analysis"
    depends_on: []
    checks:
      - ssl_present
      - ssl_expiration
      - ssl_issuer
      - certificate_chain

  # Analysis Profiles (depend on core profiles)
  headers:
    description: "Security and technical headers"
    depends_on: [http]
    checks:
      - hsts_header
      - csp_header
      - x_content_type_options
  
  content:
    description: "On-page content extraction"
    depends_on: [http]
    checks:
      - html_title
      - meta_description
      - page_size
  
  infrastructure:
    description: "Hosting and network infrastructure"
    depends_on: [dns, http]
    checks:
      - ip_geolocation
      - hosting_provider_asn
      - cdn_detection
  
  seo:
    description: "SEO-related checks"
    depends_on: [http, content]
    checks:
      - robots_txt
      - sitemap_xml
      - structured_data

  # Intelligence Profiles
  security:
    description: "Security vulnerability assessment"
    depends_on: [http, headers, ssl]
    checks:
      - exposed_files
      - security_misconfigurations
      - blacklist_check
  
  business:
    description: "Business intelligence"
    depends_on: [http, content]
    checks:
      - social_media_links
      - contact_info
      - company_codes

# Meta Profiles (combinations)
meta_profiles:
  quick-check:
    includes: [whois]
    checks: [active_status]  # Custom check
    description: "Fast filtering"
  
  standard:
    includes: [whois, dns, http, ssl, seo]
    description: "Standard technical analysis"
  
  technical-audit:
    includes: [whois, dns, http, ssl, headers, infrastructure, security]
    description: "Complete technical assessment"
  
  business-research:
    includes: [whois, dns, http, ssl, content, business, language, compliance]
    description: "Market intelligence"
  
  complete:
    includes: [all]
    description: "Everything available"
  
  monitor:
    includes: [http, ssl]
    checks: [dns_a_record, html_hash]
    description: "Lightweight recurring checks"
```

#### 6. Update CLI
Support multiple profile selection:

```bash
# Single profile
python -m src.orchestrator domains.txt --profiles dns

# Multiple profiles
python -m src.orchestrator domains.txt --profiles dns,ssl,http

# Meta profile
python -m src.orchestrator domains.txt --profiles standard

# Mix specific and meta profiles
python -m src.orchestrator domains.txt --profiles standard,clustering
```

#### 7. Update Query Tools
- `query_db.py` should show which profiles were used
- Filter results by profile combination
- Show profile-specific data

```bash
# Query by profiles used
python query_db.py latest --profiles dns,ssl

# Show profile data
python query_db.py domain example.com --show-profiles

# List available profiles
python query_db.py list-profiles
```

#### 8. Documentation
Create comprehensive profile documentation:

**`docs/TASK_MATRIX.md`** (Technical)
- Complete profile definitions with dependencies
- Check assignments for each profile
- Implementation status tracking

**`docs/TASK_PROFILES.md`** (User Guide)
- When to use each profile
- How to combine profiles
- Real-world workflow examples
- Performance characteristics

### 🧪 Validation
- [ ] Migration clears old task-based data
- [ ] Config defines all profile categories
- [ ] Orchestrator resolves profile dependencies correctly
- [ ] Core profiles can run in parallel
- [ ] Analysis profiles wait for dependencies
- [ ] Results include `profiles` and `checks_performed` metadata
- [ ] CLI accepts `--profiles` parameter with multiple values
- [ ] Query tools filter by profile combinations
- [ ] Easy to add new profiles without breaking existing ones

### 📊 Benefits
- **Performance**: One data source query serves multiple checks
- **Flexibility**: Users compose exact analysis they need
- **Maintainability**: Adding checks doesn't break profile structure
- **Natural**: Mirrors implementation (one DNS query → all records)
- **Scalable**: Easy to add new profiles or checks
- **User-Friendly**: Simple combinations like `--profiles dns,ssl`

### 💡 Usage Examples

```bash
# Fast filtering
python -m src.orchestrator domains.txt --profiles quick-check

# DNS analysis only
python -m src.orchestrator domains.txt --profiles dns

# Security audit
python -m src.orchestrator domains.txt --profiles ssl,headers,security

# Custom combination
python -m src.orchestrator domains.txt --profiles dns,infrastructure,technology

# Business intelligence
python -m src.orchestrator domains.txt --profiles whois,business,language

# Everything
python -m src.orchestrator domains.txt --profiles complete
```

### 📝 Notes for Future Implementation
When implementing, remember:
1. ✅ **Profile matrix is pre-planned** - See `docs/TASK_MATRIX.md`
2. **Implement dependency resolution** - Profiles must run in correct order
3. **Cache core data** - When `headers` and `content` both need `http`, fetch once
4. **Parallel execution** - Core profiles (`whois`, `dns`, `http`, `ssl`) can run simultaneously
5. **Update matrix as you build** - Change 🔄 to ✅ when each check is implemented
6. **Test combinations** - Verify `--profiles dns,ssl` works as expected

### 📦 Tag
```bash
git commit -m "v0.10 - task profiles and clean database schema"
git tag v0.10
git push origin main --tags
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
