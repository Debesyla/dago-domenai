# v0.10 Composable Profile System - Summary

## 🎯 What Changed

We redesigned the task/profile system from **rigid scan tiers** to **composable, data-source-based profiles**.

### ❌ Old Approach (Rejected)
```yaml
# Rigid tiers with redundant queries
basic-scan: [whois, dns, http, ssl]  # 4 API calls
full-scan: [whois, dns, http, ssl, headers, content]  # Same 4 calls AGAIN + 2 more

# Problems:
- Can't get "just DNS data"
- full-scan repeats basic-scan queries
- Inflexible combinations
```

### ✅ New Approach (Implemented in Documentation)
```yaml
# Composable profiles organized by data source
profiles:
  whois: [...]    # 1 WHOIS query → all registration data
  dns: [...]      # 1 DNS query → A, AAAA, MX, NS, TXT together
  http: [...]     # 1-2 HTTP requests → status, redirects, headers, content
  ssl: [...]      # 1 SSL handshake → cert, chain, expiration

# Usage:
--profiles dns              # Just DNS
--profiles dns,ssl          # DNS + SSL
--profiles standard         # Pre-configured combo (whois,dns,http,ssl,seo)
```

---

## 📊 Profile Categories

We now have **22 profiles** in **4 categories**:

### 🔵 Core Data Profiles (4)
Make external API calls to retrieve raw data:
- `whois` - Registration info (1 API call)
- `dns` - All DNS records (1 query set: A, AAAA, MX, NS, TXT, CNAME)
- `http` - Connectivity, redirects, response (1-2 requests)
- `ssl` - Certificate analysis (1 TLS handshake)

### 🟢 Analysis Profiles (5)
Process data from core profiles **without additional calls**:
- `headers` - HTTP security headers (depends on `http`)
- `content` - On-page content extraction (depends on `http`)
- `infrastructure` - Hosting, CDN, geolocation (depends on `dns`, `http`)
- `technology` - Tech stack detection (depends on `http`, `content`)
- `seo` - SEO checks (depends on `http`, `content`)

### 🟡 Intelligence Profiles (7)
Business insights and specialized analysis:
- `security` - Vulnerability scans (depends on `http`, `headers`, `ssl`)
- `compliance` - GDPR, privacy checks
- `business` - Company info, contacts
- `language` - Language detection, targeting
- `fingerprinting` - Screenshots, hashes
- `clustering` - Portfolio detection

### 🟠 Meta Profiles (6)
Pre-configured combinations for common workflows:
- `quick-check` - Fast filtering (whois + active)
- `standard` - General analysis (whois + dns + http + ssl + seo)
- `technical-audit` - Security focus (all technical profiles)
- `business-research` - Market intelligence (technical + business profiles)
- `complete` - Everything
- `monitor` - Change detection (minimal recurring)

---

## 🚀 Key Benefits

### 1. Performance Optimization
```python
# One DNS query returns everything:
dns_result = resolver.resolve(domain)
# → Contains: A, AAAA, MX, NS, TXT, CNAME

# Multiple profiles use this data:
dns profile: extracts all DNS records
infrastructure profile: uses A record for GeoIP
clustering profile: uses nameservers for grouping

# Result: 1 query serves 3 profiles ✅
```

### 2. Flexible Combinations
```bash
# Just what you need:
--profiles dns                    # DNS only
--profiles dns,ssl                # DNS + SSL
--profiles dns,infrastructure     # DNS + hosting analysis
--profiles ssl,headers,security   # Security audit
--profiles whois,business,language  # Business intelligence
```

### 3. Natural Dependency Management
```yaml
# Profiles declare dependencies:
headers:
  depends_on: [http]
  # Reuses HTTP response data

infrastructure:
  depends_on: [dns, http]
  # Reuses DNS records and HTTP response

# Orchestrator resolves dependencies automatically
```

### 4. Easy Extensibility
```yaml
# Adding a new check is simple:
dns:
  checks:
    - dns_a_record
    - dns_mx_records
    - dns_caa_record  # ← Add new check here

# No need to update other profiles
# No redundant queries
```

---

## 📋 Implementation Plan (v0.10)

### Files Created
1. ✅ `docs/TASK_MATRIX.md` - Technical reference with all 22 profiles
2. ✅ `docs/TASK_PROFILES.md` - User guide with examples
3. ✅ `docs/V10_SUMMARY.md` - This summary
4. ✅ Updated `docs/LAUNCH_PLAN.md` - v0.10 section rewritten
5. ✅ Updated `docs/README.md` - Navigation and quick start

### What Needs Implementation
1. 🔄 Update `config.yaml` with profile definitions
2. 🔄 Rewrite orchestrator to support profile composition
3. 🔄 Implement dependency resolution (topological sort)
4. 🔄 Update result schema to track profiles used
5. 🔄 Update CLI to accept `--profiles` parameter
6. 🔄 Update query tools to filter by profiles
7. 🔄 Database migration script
8. 🔄 Test profile combinations

---

## 💡 Usage Examples

### Example 1: Progressive Analysis
```bash
# Step 1: Quick filter 10,000 domains
python -m src.orchestrator all_domains.txt --profiles quick-check
# → 3,000 active domains

# Step 2: DNS analysis on active domains
python -m src.orchestrator active_domains.txt --profiles dns
# → Understand infrastructure

# Step 3: Complete analysis on priority domains
python -m src.orchestrator priority_domains.txt --profiles complete
```

### Example 2: Security Audit
```bash
# Just security-relevant profiles
python -m src.orchestrator company_domains.txt --profiles ssl,headers,security
```

### Example 3: Business Intelligence
```bash
# Ownership + company info + language targeting
python -m src.orchestrator competitors.txt --profiles whois,business,language
```

### Example 4: Infrastructure Research
```bash
# DNS + hosting + CDN detection
python -m src.orchestrator domains.txt --profiles dns,infrastructure
```

### Example 5: Custom Combination
```bash
# Mix and match as needed
python -m src.orchestrator domains.txt --profiles dns,ssl,technology,clustering
```

---

## 📊 Profile Statistics

| Category | Profiles | Total Checks | Currently Implemented |
|----------|----------|--------------|----------------------|
| Core Data | 4 | 39 | 7 (18%) |
| Analysis | 5 | 45 | 0 (0%) |
| Intelligence | 7 | 47 | 2 (4%) |
| Meta | 6 | - | - |
| **TOTAL** | **22** | **131** | **9 (7%)** |

### Implementation Roadmap
- **v0.10**: Profile system infrastructure (no new checks)
- **v1.1**: Complete DNS profile (11 checks)
- **v1.2**: Complete headers, content, seo profiles (~20 checks)
- **v1.3**: Complete infrastructure, technology profiles (~15 checks)
- **v2.x**: Intelligence profiles (security, business, language, compliance)
- **v3.x**: Advanced profiles (clustering, AI-powered analysis)

---

## 🎯 Why This Is Better

### Performance
**Old way:**
```bash
basic-scan: Query DNS for A record
full-scan: Query DNS AGAIN for A record + MX record
```

**New way:**
```bash
dns profile: Query ONCE → get A, MX, NS, TXT, AAAA together
# Both basic and full analysis use same data
```

### Flexibility
**Old way:**
```bash
# Want just DNS data? Run full-scan and ignore 40 other checks
# Want SSL + DNS? Not possible, must run full-scan
```

**New way:**
```bash
--profiles dns          # Just DNS
--profiles dns,ssl      # DNS + SSL
--profiles dns,infrastructure,technology  # Custom combo
```

### Maintainability
**Old way:**
```python
# Adding MX check means updating:
- basic-scan profile
- full-scan profile  
- research-scan profile
# Risk of inconsistency
```

**New way:**
```python
# Add MX check to dns profile only:
dns:
  checks:
    - dns_a_record
    - dns_mx_records  # ← Add here
    
# All profiles using dns automatically get it
```

---

## 🔄 Migration Notes

### For Users
- Change `--task basic-scan` → `--profiles standard`
- More flexible: Can now request specific data sources
- Results now show which profiles were used
- Can combine profiles: `--profiles dns,ssl,business`

### For Developers
- Organize checks by data source, not by tier
- One check module per profile
- Declare profile dependencies in config
- Core profiles can run in parallel
- Analysis profiles wait for dependencies

---

## 📚 Documentation Structure

```
docs/
├── README.md                     # Navigation hub
├── TASK_MATRIX.md                # Technical: All 22 profiles with dependencies
├── TASK_PROFILES.md              # User guide: When to use which profile
├── PLANNED_CHECKS.md             # Catalog: All 131+ checks by tier
├── V10_SUMMARY.md                # This file: What changed and why
├── V10_TASK_PROFILES_DESIGN.md   # Original design document
└── LAUNCH_PLAN.md                # Updated: v0.10 implementation plan
```

---

## ✅ Validation Checklist

When implementing v0.10:

- [ ] Config defines all 22 profiles with dependencies
- [ ] Orchestrator resolves profile dependencies (topological sort)
- [ ] Core profiles (`whois`, `dns`, `http`, `ssl`) can run in parallel
- [ ] Analysis profiles wait for dependencies
- [ ] CLI accepts `--profiles dns,ssl,http` syntax
- [ ] Results include `profiles` array in metadata
- [ ] Results include `checks_performed` array
- [ ] Query tools filter by profile combinations
- [ ] `--profiles standard` expands to `whois,dns,http,ssl,seo`
- [ ] Data reuse works: `headers` and `content` share `http` data
- [ ] Adding new check to profile doesn't break other profiles
- [ ] Documentation matches implementation

---

## 🎓 Next Steps

### For v0.10 Implementation
1. Create profile configuration in `config.yaml`
2. Implement dependency resolution in orchestrator
3. Update result schema with profiles metadata
4. Update CLI to support `--profiles` parameter
5. Test combinations: `--profiles dns,ssl`, `--profiles standard`
6. Verify data reuse works (no redundant queries)

### For v1.x
1. Implement remaining Core Data profile checks (DNS, WHOIS full)
2. Implement Analysis profiles (headers, content, infrastructure)
3. As each check is implemented, update TASK_MATRIX.md (🔄 → ✅)
4. Test profile compositions with real data

---

**Key Takeaway:** We moved from "scan depths" (basic/full/research) to "data sources" (dns/http/ssl/whois) which mirrors how data is actually retrieved and enables efficient, flexible combinations. 🎯
