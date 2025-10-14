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

# 🚀 FUTURE VERSIONS — MVP & Beyond

**Strategy:**
- **v1.x** = Core Data Profiles (MVP with 4 essential profiles)
- **v2.x** = Frontend Dashboard (from minimal to full-featured)
- **v3.x** = Analysis Profiles (processing core data)
- **v4.x** = Intelligence Profiles (business insights & AI)
- **v5.x+** = Advanced Features (clustering, monitoring, APIs)

---

## 🔵 PHASE 1: Core Data Profiles (MVP)

These versions complete the **Core Data** layer - the foundation that makes external API calls.

---

## 🟣 Version 1.1 — WHOIS Profile (Complete)

### 🎯 Goal
Complete all WHOIS-related checks from v0.8 placeholders.

### 📋 Tasks
1. Implement full `checks/whois_check.py`:
   - ✅ Registration status (already working from v0.8)
   - Registrar name and IANA ID
   - Registration date
   - Expiration date
   - Updated date
   - Registrant organization
   - Registry status codes
   - Privacy protection detection
   - Domain age calculation (from registration date)

2. Add WHOIS data enrichment:
   - Detect registrar transfers (compare WHOIS history if available)
   - Flag expiring domains (< 30 days)
   - Identify high-risk registrars

3. Update `whois` profile in `config.yaml`:
   - All 10 WHOIS checks marked as implemented

### 🧪 Validation
- `--profiles whois` returns complete registration data
- Correctly identifies: registrar, dates, privacy protection
- Domain age calculated accurately
- Handles WHOIS rate limits gracefully

### 📦 Tag
```bash
git commit -m "v1.1 - complete WHOIS profile implementation"
git tag v1.1
```

---

## 🟣 Version 1.2 — DNS Profile (Complete)

### 🎯 Goal
Implement comprehensive DNS resolution covering all record types.

### 📋 Tasks
1. Implement full `checks/dns_check.py`:
   - A records (IPv4 addresses)
   - AAAA records (IPv6 addresses)
   - MX records (mail servers)
   - NS records (nameservers)
   - TXT records (SPF, DKIM, verification tokens)
   - CNAME records
   - SOA record (Start of Authority)
   - DNS propagation check (query multiple DNS servers)
   - DNSSEC validation

2. Add DNS analysis:
   - Identify DNS provider (Cloudflare, Route53, etc.)
   - Detect DNS-based CDN usage
   - Check for missing critical records (MX for business domains)
   - Validate SPF/DKIM configuration

3. Update `dns` profile in `config.yaml`:
   - All 11 DNS checks marked as implemented

### 🧪 Validation
- `--profiles dns` returns all DNS record types
- Single DNS query retrieves all records efficiently
- Correctly identifies DNS provider
- Handles DNS timeouts and NXDOMAIN gracefully

### 📦 Tag
```bash
git commit -m "v1.2 - complete DNS profile implementation"
git tag v1.2
```

---

## 🟣 Version 1.3 — HTTP Profile (Complete)

### 🎯 Goal
Enhance HTTP connectivity checks with full redirect analysis and performance metrics.

### 📋 Tasks
1. Expand `checks/http_check.py` (building on v0.4-0.5):
   - ✅ HTTP status code (already working)
   - ✅ Redirect chain (from v0.5)
   - Response time measurement
   - HTTPS availability check
   - HTTP/2 or HTTP/3 support detection
   - Compression support (gzip, brotli)
   - Response size
   - Final URL after redirects
   - Detect redirect loops
   - Mobile redirect detection (user-agent based)

2. Add HTTP behavior analysis:
   - Identify redirect type (301 permanent vs 302 temporary)
   - Detect forced HTTPS upgrades
   - Check for domain parking pages
   - Measure Time to First Byte (TTFB)

3. Update `http` profile in `config.yaml`:
   - All 10 HTTP checks marked as implemented

### 🧪 Validation
- `--profiles http` returns full connectivity data
- Redirect chains tracked accurately
- Performance metrics captured
- Handles timeouts and connection errors

### 📦 Tag
```bash
git commit -m "v1.3 - complete HTTP profile implementation"
git tag v1.3
```

---

## 🟣 Version 1.4 — SSL Profile (Complete)

### 🎯 Goal
Implement comprehensive SSL/TLS certificate analysis and security checks.

### 📋 Tasks
1. Expand `checks/ssl_check.py` (building on v0.5):
   - ✅ SSL presence (already working)
   - Certificate expiration date
   - Certificate issuer (CA)
   - Subject Alternative Names (SANs)
   - Certificate chain validation
   - SSL/TLS protocol versions supported
   - Cipher suite analysis
   - Certificate transparency logs
   - OCSP stapling
   - Self-signed certificate detection

2. Add SSL security analysis:
   - Flag weak ciphers (3DES, RC4)
   - Detect outdated TLS versions (TLS 1.0, 1.1)
   - Check for certificate mismatch
   - Validate certificate against domain name
   - Identify wildcard certificates
   - Extract organization from certificate

3. Update `ssl` profile in `config.yaml`:
   - All 10 SSL checks marked as implemented

### 🧪 Validation
- `--profiles ssl` returns complete certificate data
- Security issues flagged correctly
- Handles domains without SSL gracefully
- Certificate chain validated properly

### 📦 Tag
```bash
git commit -m "v1.4 - complete SSL profile implementation"
git tag v1.4
```

---

## 🟣 Version 1.5 — MVP Polish & Optimization

### 🎯 Goal
Optimize Core Profile performance and prepare for v2.0 frontend.

### 📋 Tasks
1. Performance optimization:
   - Parallel execution of all 4 core profiles
   - Connection pooling for HTTP requests
   - DNS query caching (TTL-aware)
   - Retry logic with exponential backoff

2. Error handling improvements:
   - Graceful degradation (partial results if some checks fail)
   - Detailed error messages in results
   - Rate limit detection and handling

3. Add core meta profiles:
   - `quick-check` - WHOIS + active detection only
   - `standard` - All 4 core profiles (whois, dns, http, ssl)
   - `monitor` - Lightweight recurring checks (http + ssl expiry)

4. Export and reporting:
   - JSON export with profile metadata
   - CSV export for spreadsheet analysis
   - Summary statistics (success rate, avg duration)

5. Documentation:
   - User guide for all core profiles
   - Performance benchmarks
   - API documentation (prepare for v2.0 frontend)

### 🧪 Validation
- `--profiles standard` completes in < 5 seconds
- All 4 core profiles working independently and in combination
- Error handling robust across all scenarios
- Export formats clean and usable

### 📦 Tag
```bash
git commit -m "v1.5 - MVP complete with optimized core profiles"
git tag v1.5
```

---

## 🎨 PHASE 2: Frontend Dashboard

Building a web interface to visualize and explore domain data.

---

## 🟣 Version 2.0 — Minimal Frontend (FastAPI Backend)

### 🎯 Goal
Create basic REST API and minimal web interface to view domain results.

### 📋 Tasks
1. Setup FastAPI backend:
   - `/api/domains` - List all domains
   - `/api/domains/{domain}` - Get domain details
   - `/api/scan` - Trigger new scan
   - `/api/profiles` - List available profiles
   - CORS configuration for frontend

2. Create minimal HTML/JS frontend:
   - Simple domain list view
   - Domain detail page showing all checks
   - Search functionality
   - Trigger scan from UI

3. Database API layer:
   - Query builder for domain searches
   - Pagination support
   - Filter by profile or check status

4. Authentication (optional):
   - Simple API key system
   - Rate limiting

### 🧪 Validation
- API endpoints return JSON correctly
- Frontend displays domain data
- Can trigger scans from UI
- Search works across domains

### 📦 Tag
```bash
git commit -m "v2.0 - minimal frontend with FastAPI backend"
git tag v2.0
```

---

## 🟣 Version 2.1 — Dashboard UI & Filtering

### 🎯 Goal
Add professional dashboard interface with filtering and sorting.

### 📋 Tasks
1. Improve frontend UI:
   - Modern CSS framework (Tailwind or Bootstrap)
   - Responsive design (mobile-friendly)
   - Domain cards with status badges
   - Profile-specific views

2. Advanced filtering:
   - Filter by: active/inactive, registered/unregistered
   - Filter by profile used
   - Filter by check results (e.g., "has SSL", "no robots.txt")
   - Date range filtering

3. Sorting & pagination:
   - Sort by: domain name, last updated, status
   - Configurable page size
   - Infinite scroll or pagination

4. Bulk operations:
   - Select multiple domains
   - Trigger bulk scans
   - Bulk export

### 🧪 Validation
- Filtering works smoothly
- UI responsive on mobile
- Bulk operations handle 100+ domains
- Performance remains good with 10,000+ domains

### 📦 Tag
```bash
git commit -m "v2.1 - dashboard UI with filtering"
git tag v2.1
```

---

## 🟣 Version 2.2 — Charts & Analytics

### 🎯 Goal
Add visual analytics and statistics dashboards.

### 📋 Tasks
1. Implement Chart.js or similar:
   - Domain distribution by status (active/inactive/unregistered)
   - Registrar distribution (pie chart)
   - SSL issuer distribution
   - Hosting provider distribution (from DNS/IP data)
   - Domain age histogram

2. Statistics dashboard:
   - Total domains scanned
   - Success/failure rates
   - Average scan duration
   - Most common registrars
   - Top hosting providers
   - SSL expiration alerts

3. Timeline views:
   - Scan history over time
   - Domain additions over time
   - Status changes tracking

4. Export statistics:
   - Download charts as PNG
   - Export stats to PDF report

### 🧪 Validation
- Charts render correctly with real data
- Statistics accurate
- Dashboard loads fast even with large datasets
- Exports work properly

### 📦 Tag
```bash
git commit -m "v2.2 - analytics dashboard with charts"
git tag v2.2
```

---

## 🟣 Version 2.3 — Performance & UX Polish

### 🎯 Goal
Optimize frontend performance and improve user experience.

### 📋 Tasks
1. Performance optimization:
   - Implement caching (Redis or in-memory)
   - Database query optimization
   - Lazy loading for large lists
   - API response compression

2. UX improvements:
   - Real-time scan progress (WebSocket updates)
   - Toast notifications for events
   - Keyboard shortcuts
   - Dark mode support
   - Export profiles (save filter combinations)

3. Advanced features:
   - Domain comparison view (side-by-side)
   - Scan scheduling (cron-like interface)
   - Custom domain lists (tags/categories)
   - Notes/comments on domains

4. Error handling:
   - User-friendly error messages
   - Retry failed scans from UI
   - Debug mode for troubleshooting

### 🧪 Validation
- Frontend feels snappy (< 100ms interactions)
- Real-time updates work smoothly
- Dark mode renders correctly
- All UX features intuitive

### 📦 Tag
```bash
git commit -m "v2.3 - frontend performance & UX polish"
git tag v2.3
```

---

## 🟢 PHASE 3: Analysis Profiles

Processing core data without additional API calls.

---

## 🟣 Version 3.0 — Headers Profile

### 🎯 Goal
Analyze HTTP security and technical headers.

### 📋 Tasks
1. Implement `checks/headers_check.py`:
   - Depends on `http` profile (reuses HTTP response)
   - HSTS (Strict-Transport-Security)
   - CSP (Content-Security-Policy)
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Referrer-Policy
   - Permissions-Policy

2. Header analysis:
   - Security score based on headers
   - Missing critical headers flagged
   - Technology hints from headers (Server, X-Powered-By)

### 📦 Tag
```bash
git commit -m "v3.0 - headers profile implementation"
git tag v3.0
```

---

## 🟣 Version 3.1 — Content Profile

### 🎯 Goal
Extract and analyze on-page content.

### 📋 Tasks
1. Implement `checks/content_check.py`:
   - Depends on `http` profile (reuses HTML response)
   - HTML title extraction
   - Meta description
   - Meta keywords
   - Open Graph tags
   - Twitter Card tags
   - Page size (HTML, CSS, JS)
   - Word count
   - Language from `<html lang>`

2. Content analysis:
   - Detect missing important meta tags
   - Title/description length validation
   - Identify duplicate content patterns

### 📦 Tag
```bash
git commit -m "v3.1 - content profile implementation"
git tag v3.1
```

---

## 🟣 Version 3.2 — Infrastructure Profile

### 🎯 Goal
Analyze hosting and network infrastructure.

### 📋 Tasks
1. Implement `checks/infrastructure_check.py`:
   - Depends on `dns`, `http` profiles
   - IP geolocation (GeoIP database)
   - ASN lookup (hosting provider identification)
   - Reverse DNS lookup
   - CDN detection (Cloudflare, Akamai, etc.)
   - Shared hosting detection
   - IPv6 support check

2. Infrastructure insights:
   - Hosting country
   - Provider reputation
   - CDN performance score

### 📦 Tag
```bash
git commit -m "v3.2 - infrastructure profile implementation"
git tag v3.2
```

---

## 🟣 Version 3.3 — Technology Profile

### 🎯 Goal
Detect technologies, frameworks, and CMS platforms.

### 📋 Tasks
1. Implement `checks/technology_check.py`:
   - Depends on `http`, `content` profiles
   - CMS detection (WordPress, Joomla, Drupal, etc.)
   - Framework detection (React, Vue, Angular, Laravel)
   - Analytics detection (Google Analytics, Matomo)
   - Tag manager detection
   - JavaScript libraries (jQuery, Bootstrap)
   - Web server detection (Nginx, Apache)

2. Technology patterns:
   - Pattern matching from HTML/headers
   - Version detection where possible
   - Technology stack summary

### 📦 Tag
```bash
git commit -m "v3.3 - technology profile implementation"
git tag v3.3
```

---

## 🟣 Version 3.4 — SEO Profile (Complete)

### 🎯 Goal
Complete all SEO-related checks.

### 📋 Tasks
1. Expand `checks/seo_check.py`:
   - ✅ robots.txt (from v0.5)
   - ✅ sitemap.xml (from v0.5)
   - Favicon presence
   - Canonical tags
   - Structured data (schema.org)
   - hreflang tags
   - URL structure quality
   - Image alt tags
   - H1-H6 heading structure

2. SEO analysis:
   - SEO score calculation
   - Missing SEO elements flagged
   - Best practice recommendations

### 📦 Tag
```bash
git commit -m "v3.4 - complete SEO profile implementation"
git tag v3.4
```

---

## 🟡 PHASE 4: Intelligence Profiles

Business insights and advanced analysis.

---

## 🟣 Version 4.0 — Security Profile

### 🎯 Goal
Security vulnerability scanning and risk assessment.

### 📋 Tasks
1. Implement `checks/security_check.py`:
   - Depends on `http`, `headers`, `ssl`, `technology`
   - Exposed sensitive files (.git, .env, .config)
   - Security header misconfigurations
   - Known vulnerable technology versions
   - Blacklist checks (DNSBL, Google Safe Browsing)
   - Phishing/malware flags
   - VPN/proxy IP detection

2. Security scoring:
   - Risk score (0-100)
   - Critical issues highlighted
   - Remediation suggestions

### 📦 Tag
```bash
git commit -m "v4.0 - security profile implementation"
git tag v4.0
```

---

## 🟣 Version 4.1 — Business Profile

### 🎯 Goal
Extract business intelligence and contact information.

### 📋 Tasks
1. Implement `checks/business_check.py`:
   - Depends on `http`, `content`
   - Social media links (Facebook, LinkedIn, Twitter)
   - Contact info extraction (email, phone)
   - Company codes / VAT numbers
   - Lithuanian city mentions
   - Currency detection
   - Social proof elements (testimonials, reviews)
   - AI chatbot presence

2. Business insights:
   - Business type classification
   - Market segment detection
   - Contact completeness score

### �� Tag
```bash
git commit -m "v4.1 - business profile implementation"
git tag v4.1
```

---

## 🟣 Version 4.2 — Compliance Profile

### 🎯 Goal
GDPR and privacy compliance checking.

### 📋 Tasks
1. Implement `checks/compliance_check.py`:
   - Depends on `http`, `content` (needs headless browser)
   - Cookie banner detection
   - GDPR compliance signals
   - Cookie consent mechanism
   - Privacy policy link
   - Terms of service link
   - Data processing information

2. Setup headless browser:
   - Playwright or Puppeteer integration
   - JavaScript execution for cookie detection
   - Screenshot capability (prepare for v4.3)

### 📦 Tag
```bash
git commit -m "v4.2 - compliance profile implementation"
git tag v4.2
```

---

## 🟣 Version 4.3 — Language Profile

### 🎯 Goal
Language detection and audience targeting analysis.

### 📋 Tasks
1. Implement `checks/language_check.py`:
   - Depends on `content`
   - Primary language detection (NLP)
   - Lithuanian audience targeting detection
   - Multilingual setup detection
   - Language variants (hreflang analysis)
   - Language mismatch detection
   - Lithuanian vs English ratio
   - Keyword extraction
   - Topic extraction

2. NLP integration:
   - Use spaCy or similar for language detection
   - Text classification model
   - Topic modeling

### 📦 Tag
```bash
git commit -m "v4.3 - language profile implementation"
git tag v4.3
```

---

## 🟣 Version 4.4 — Fingerprinting Profile

### 🎯 Goal
Digital fingerprinting for domain identification and comparison.

### 📋 Tasks
1. Implement `checks/fingerprinting_check.py`:
   - Depends on `http` (+ headless browser)
   - Screenshot capture
   - Homepage HTML hash
   - Favicon hash
   - Parked domain detection
   - For-sale banner detection

2. Visual analysis:
   - Perceptual hashing for screenshots
   - Favicon similarity detection
   - Template recognition

### 📦 Tag
```bash
git commit -m "v4.4 - fingerprinting profile implementation"
git tag v4.4
```

---

## 🟣 Version 4.5 — Clustering Profile

### 🎯 Goal
Portfolio and relationship detection between domains.

### 📋 Tasks
1. Implement `checks/clustering_check.py`:
   - Depends on `dns`, `ssl`, `whois`, `technology`, `fingerprinting`
   - Shared IP address detection
   - Shared analytics ID (GA, GTM)
   - SSL organization grouping
   - Shared hosting cluster
   - Favicon-based clustering
   - CSS/JS library similarity

2. Relationship graph:
   - Build domain relationship database
   - Cluster visualization in frontend
   - Portfolio detection algorithms

### �� Tag
```bash
git commit -m "v4.5 - clustering profile implementation"
git tag v4.5
```

---

## 🚀 PHASE 5: Advanced Features

---

## 🟣 Version 5.0 — AI-Assisted Classification

### 🎯 Goal
Use LLM for intelligent domain classification and summarization.

### 📋 Tasks
1. LLM integration (OpenAI, Anthropic, or local model):
   - Read homepage content
   - Classify domain type (e-shop, blog, company, parked, etc.)
   - Generate one-sentence summary
   - Detect product/service categories
   - Business model classification

2. AI features in frontend:
   - Show AI summaries on domain cards
   - AI-powered search (semantic)
   - Category-based filtering

### 📦 Tag
```bash
git commit -m "v5.0 - AI-assisted classification"
git tag v5.0
```

---

## 🟣 Version 5.1 — External API Enrichment

### 🎯 Goal
Integrate third-party data sources for enrichment.

### 📋 Tasks
1. API integrations:
   - Ahrefs / SEMrush (traffic, backlinks, domain authority)
   - SimilarWeb (traffic estimates)
   - VirusTotal (security reputation)
   - WHOIS history services

2. Enrichment scoring:
   - Combined domain quality score
   - Authority metrics
   - Risk assessment

### 📦 Tag
```bash
git commit -m "v5.1 - external API enrichment"
git tag v5.1
```

---

## 🟣 Version 5.2 — Monitoring & Change Detection

### 🎯 Goal
Continuous monitoring mode with change alerts.

### 📋 Tasks
1. Monitoring system:
   - Scheduled recurring scans
   - Change detection (compare with previous scan)
   - Alert system (email, webhook)
   - Monitor profile (lightweight recurring checks)

2. Change tracking:
   - SSL expiration warnings
   - DNS changes
   - Content changes (hash comparison)
   - Status changes (active → inactive)

### 📦 Tag
```bash
git commit -m "v5.2 - monitoring & change detection"
git tag v5.2
```

---

## 🟣 Version 5.3+ — Future Ideas

- **Distributed processing cluster** - Scale to millions of domains
- **Public API** - Let others query your domain data
- **Domain suggestion engine** - Find similar or available domains
- **Company registry integration** - Match domains to Lithuanian companies
- **Market intelligence reports** - Generate PDF reports for business research
- **Mobile app** - iOS/Android companion app
- **Browser extension** - Analyze domain while browsing
- **Webhook integrations** - Zapier, n8n, etc.

---

**End of Roadmap**

Each version builds upon previous work incrementally.  
Commit, tag, and validate before proceeding to next version.
