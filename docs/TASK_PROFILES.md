# Task Profiles - User Guide

This guide explains the **composable profile system** where you can mix and match profiles to create custom scanning strategies.

---

## 🎯 What's Different About Our Profiles?

### Traditional Approach (❌ Inefficient)
Most domain scanners have rigid tiers like "basic scan" or "full scan":
- Basic scan: Makes 5 different API calls
- Full scan: Makes the SAME 5 calls again + 10 more
- Want just DNS data? Too bad, run the whole thing

### Our Approach (✅ Efficient & Composable)
We organize profiles by **data source**, not scan depth:
- `dns` profile: ONE query → all DNS records (A, MX, NS, TXT, etc.)
- `whois` profile: ONE query → all registration data
- `ssl` profile: ONE handshake → all certificate info

**You combine them:**
```bash
# Just need DNS and WHOIS?
--profiles dns,whois

# Need everything technical?
--profiles dns,whois,http,ssl,headers,infrastructure

# Business intelligence only?
--profiles business,language,compliance
```

---

## 📊 Profile Categories

We have **4 categories** of profiles:

### 🔵 Core Data Profiles
Extract raw data (make external API calls)
- `whois` `dns` `http` `ssl`

### 🟢 Analysis Profiles  
Process data from core profiles (no additional calls)
- `headers` `content` `infrastructure` `technology` `seo`

### 🟡 Intelligence Profiles
Business insights and specialized analysis
- `security` `compliance` `business` `language` `fingerprinting` `clustering`

### 🟠 Meta Profiles
Pre-configured combos for common tasks
- `quick-check` `standard` `technical-audit` `business-research` `complete` `monitor`

---

## 🔵 Core Data Profiles

These make the actual API calls to external services.

### `whois`
**What it does:** Queries WHOIS servers for registration information  
**Duration:** 0.5-1 second  
**Data returned:**
- Registration status (registered vs available)
- Registrar name and ID
- Registration, expiration, updated dates
- Registrant organization
- Privacy protection status
- Domain age

**Use when:** You need ownership and registration info

```bash
python3 -m src.orchestrator domains.txt --profiles whois
```

---

### `dns`
**What it does:** Resolves all DNS record types  
**Duration:** 0.3-0.8 seconds  
**Data returned:**
- A records (IPv4)
- AAAA records (IPv6)
- MX records (mail servers)
- NS records (nameservers)
- TXT records (SPF, DKIM, DMARC)
- CNAME records

**Use when:** You need network and email infrastructure info

```bash
python3 -m src.orchestrator domains.txt --profiles dns
```

---

### `http`
**What it does:** Makes HTTP/HTTPS requests  
**Duration:** 1-3 seconds  
**Data returned:**
- HTTP status code
- Redirect chain
- Final destination URL
- Response time
- HTTPS availability
- HTTP/2 or HTTP/3 support

**Use when:** You need connectivity and redirect info

```bash
python3 -m src.orchestrator domains.txt --profiles http
```

---

### `ssl`
**What it does:** Performs TLS handshake  
**Duration:** 0.5-1.5 seconds  
**Data returned:**
- Certificate validity
- Expiration date
- Issuer (Certificate Authority)
- Validation type (DV/OV/EV)
- Certificate chain
- Subject information

**Use when:** You need SSL certificate info

```bash
python3 -m src.orchestrator domains.txt --profiles ssl
```

---

## 🟢 Analysis Profiles

These analyze data from core profiles **without making additional calls**.

### `headers`
**Depends on:** `http`  
**Duration:** < 0.1 seconds  
**What it checks:**
- Security headers (HSTS, CSP, X-Frame-Options)
- Server software detection
- Configuration issues

**Use when:** Security posture assessment

```bash
python3 -m src.orchestrator domains.txt --profiles http,headers
```

---

### `content`
**Depends on:** `http`  
**Duration:** 0.2-0.5 seconds  
**What it extracts:**
- HTML title and meta description
- Language and charset
- Canonical URL
- Page size and structure
- External links

**Use when:** On-page SEO or content analysis

```bash
python3 -m src.orchestrator domains.txt --profiles http,content
```

---

### `infrastructure`
**Depends on:** `dns`, `http`  
**Duration:** 0.5-1 second (GeoIP lookup)  
**What it determines:**
- IP geolocation (country/region)
- Hosting provider (ASN)
- Cloud hosting detection
- CDN usage
- Load balancer setup

**Use when:** Understanding hosting architecture

```bash
python3 -m src.orchestrator domains.txt --profiles dns,http,infrastructure
```

---

### `technology`
**Depends on:** `http`, `content`  
**Duration:** 0.2-0.5 seconds  
**What it detects:**
- CMS (WordPress, Drupal, etc.)
- JavaScript frameworks
- Analytics platforms
- Technology stack

**Use when:** Tech stack fingerprinting

```bash
python3 -m src.orchestrator domains.txt --profiles http,content,technology
```

---

### `seo`
**Depends on:** `http`, `content`  
**Duration:** 1-2 seconds (fetches robots.txt, sitemap)  
**What it checks:**
- robots.txt and sitemap.xml
- Structured data (schema.org)
- SEO metadata
- URL cleanliness

**Use when:** SEO audit

```bash
python3 -m src.orchestrator domains.txt --profiles http,content,seo
```

---

## 🟡 Intelligence Profiles

Advanced insights for research and compliance.

### `security`
**Depends on:** `http`, `headers`, `ssl`, `technology`  
**Duration:** 2-5 seconds  
**What it checks:**
- Vulnerability scans (exposed files)
- Security misconfigurations
- Blacklist presence
- Phishing/malware flags

**Use when:** Security assessment

```bash
python3 -m src.orchestrator domains.txt --profiles http,ssl,headers,technology,security
```

---

### `business`
**Depends on:** `http`, `content`  
**Duration:** 0.3-0.8 seconds  
**What it extracts:**
- Social media links
- Contact information
- Company codes / VAT numbers
- Lithuanian business identifiers

**Use when:** Business intelligence gathering

```bash
python3 -m src.orchestrator domains.txt --profiles http,content,business
```

---

### `language`
**Depends on:** `content`  
**Duration:** 0.5-1 second  
**What it analyzes:**
- Language detection
- Lithuanian audience signals
- Multilingual setup
- Keyword extraction

**Use when:** Market targeting analysis

```bash
python3 -m src.orchestrator domains.txt --profiles http,content,language
```

---

### `compliance`
**Depends on:** `http`, `content` (requires headless browser)  
**Duration:** 3-5 seconds  
**What it checks:**
- Cookie banners
- GDPR compliance
- Privacy policy presence
- Terms of service

**Use when:** Regulatory compliance audit

```bash
python3 -m src.orchestrator domains.txt --profiles http,content,compliance
```

---

### `fingerprinting`
**Depends on:** `http` (+ headless browser)  
**Duration:** 5-10 seconds  
**What it captures:**
- Screenshots
- Homepage HTML hash
- Favicon hash
- Parked domain detection

**Use when:** Visual analysis or change detection

```bash
python3 -m src.orchestrator domains.txt --profiles http,fingerprinting
```

---

### `clustering`
**Depends on:** `dns`, `ssl`, `whois`, `technology`, `fingerprinting`  
**Duration:** 0.1-0.3 seconds (database queries)  
**What it detects:**
- Shared infrastructure (IPs, hosting)
- Common ownership (analytics IDs, SSL org)
- Portfolio relationships

**Use when:** Finding related domains

```bash
python3 -m src.orchestrator domains.txt --profiles dns,ssl,whois,technology,fingerprinting,clustering
```

---

## 🟠 Meta Profiles

Pre-configured combinations for common workflows.

### `quick-check`
**Composition:** `whois` + active detection  
**Duration:** 1-2 seconds  
**Purpose:** Fast filtering for bulk lists

**Use case:** You have 10,000 domains and want to filter down to only registered, active ones.

```bash
python3 -m src.orchestrator all_domains.txt --profiles quick-check
```

---

### `standard`
**Composition:** `whois` + `dns` + `http` + `ssl` + `seo`  
**Duration:** 5-10 seconds  
**Purpose:** General health check

**Use case:** Standard analysis of curated domain list.

```bash
python3 -m src.orchestrator my_domains.txt --profiles standard
```

---

### `technical-audit`
**Composition:** All technical profiles  
**Duration:** 15-30 seconds  
**Purpose:** Complete technical assessment

**Use case:** Security and infrastructure audit.

```bash
python3 -m src.orchestrator company_domains.txt --profiles technical-audit
```

---

### `business-research`
**Composition:** Technical + business intelligence profiles  
**Duration:** 30-60 seconds  
**Purpose:** Market research

**Use case:** Competitor analysis or market intelligence.

```bash
python3 -m src.orchestrator competitors.txt --profiles business-research
```

---

### `complete`
**Composition:** All available profiles  
**Duration:** 60-120 seconds  
**Purpose:** Everything

**Use case:** Deep domain intelligence.

```bash
python3 -m src.orchestrator priority_domains.txt --profiles complete
```

---

### `monitor`
**Composition:** Minimal change detection  
**Duration:** 2-3 seconds  
**Purpose:** Track changes over time

**Use case:** Recurring scans to detect when things change.

```bash
python3 -m src.orchestrator monitored.txt --profiles monitor
```

---

## 🔄 Choosing Profiles

### By Need

**"I need to filter 10,000 domains fast"**
```bash
--profiles quick-check
```

**"I need DNS records only"**
```bash
--profiles dns
```

**"I need security audit"**
```bash
--profiles ssl,headers,security
```

**"I need business intelligence"**
```bash
--profiles whois,business,language,compliance
```

**"I need everything"**
```bash
--profiles complete
```

### By Data Source

**Network Infrastructure:**
```bash
--profiles dns,infrastructure
```

**Web Server:**
```bash
--profiles http,headers,content,seo
```

**Ownership:**
```bash
--profiles whois,ssl,clustering
```

**Content Analysis:**
```bash
--profiles http,content,language,technology
```

---

## 💡 Advanced Usage

### Example 1: DNS + Infrastructure Analysis
```bash
# Get all DNS records and hosting info
python3 -m src.orchestrator domains.txt --profiles dns,infrastructure
```

**Why this works:** `infrastructure` uses data from `dns` (no redundant queries)

---

### Example 2: Security-Focused Scan
```bash
# SSL + security headers + vulnerability checks
python3 -m src.orchestrator domains.txt --profiles ssl,http,headers,security
```

**Why this works:** Each profile contributes specific security checks

---

### Example 3: Business Intelligence
```bash
# Registration + company info + language targeting
python3 -m src.orchestrator domains.txt --profiles whois,http,content,business,language
```

**Why this works:** Combines ownership data with on-page business signals

---

### Example 4: Progressive Analysis
```bash
# Step 1: Quick filter
python3 -m src.orchestrator all_domains.txt --profiles quick-check

# Step 2: DNS on active domains
python3 -m src.orchestrator active_domains.txt --profiles dns

# Step 3: Full analysis on priority domains
python3 -m src.orchestrator priority_domains.txt --profiles complete
```

---

### Example 5: Monitoring Setup
```bash
# Initial baseline with standard profile
python3 -m src.orchestrator monitored.txt --profiles standard

# Daily checks with monitor profile
python3 -m src.orchestrator monitored.txt --profiles monitor --schedule daily
```

---

## 📊 Performance Guide

### Single Profile Duration

| Profile | Duration | API Calls |
|---------|----------|-----------|
| `whois` | 0.5-1s | 1 |
| `dns` | 0.3-0.8s | 1 |
| `http` | 1-3s | 1-2 |
| `ssl` | 0.5-1.5s | 1 |
| `headers` | <0.1s | 0 |
| `content` | 0.2-0.5s | 0 |
| `seo` | 1-2s | 2 |
| `infrastructure` | 0.5-1s | 1-2 |
| `technology` | 0.2-0.5s | 0 |
| `security` | 2-5s | 3-5 |
| `business` | 0.3-0.8s | 0 |
| `language` | 0.5-1s | 0 |
| `compliance` | 3-5s | 0* |
| `fingerprinting` | 5-10s | 1-2 |
| `clustering` | 0.1-0.3s | 0 |

*Requires headless browser

### Combined Profile Duration

**Core Data Only:**
```bash
--profiles whois,dns,http,ssl
Duration: ~3-6 seconds
```

**Standard Meta:**
```bash
--profiles standard
Duration: ~5-10 seconds
```

**Technical Audit:**
```bash
--profiles technical-audit
Duration: ~15-30 seconds
```

**Complete:**
```bash
--profiles complete
Duration: ~60-120 seconds
```

### Batch Processing (1000 domains, 10 workers)

| Profile Combo | Total Time | Per Domain |
|---------------|------------|------------|
| `quick-check` | 3-5 min | 1-2s |
| `whois,dns` | 5-8 min | 2-3s |
| `standard` | 15-20 min | 5-10s |
| `technical-audit` | 1-2 hours | 15-30s |
| `complete` | 4-5 hours | 60-120s |

---

## � Real-World Workflows

### Workflow 1: Domain Discovery & Research
```bash
# Step 1: Get all .lt domains (external source)
# domains_all.txt = 50,000 domains

# Step 2: Quick filter to active domains
python3 -m src.orchestrator domains_all.txt --profiles quick-check
# Result: domains_active.txt = 15,000 domains (30% active rate)

# Step 3: Get DNS + infrastructure for active domains
python3 -m src.orchestrator domains_active.txt --profiles dns,infrastructure
# Result: Know hosting patterns, geographic distribution

# Step 4: Deep research on Lithuanian-hosted domains
python3 -m src.orchestrator domains_lt_hosted.txt --profiles business-research
# Result: Company info, language targeting, business intelligence
```

### Workflow 2: Security Audit
```bash
# Quick filter to registered domains
python3 -m src.orchestrator company_domains.txt --profiles quick-check

# Full technical audit
python3 -m src.orchestrator company_domains_active.txt --profiles technical-audit

# Deep security scan on critical domains
python3 -m src.orchestrator critical_domains.txt --profiles ssl,headers,security,technology
```

### Workflow 3: Competitor Analysis
```bash
# Get complete picture of 5 competitors
python3 -m src.orchestrator competitors.txt --profiles complete

# Find their portfolio through clustering
python3 -m src.orchestrator discovered_related.txt --profiles dns,ssl,clustering
```

### Workflow 4: Portfolio Monitoring
```bash
# Initial comprehensive baseline
python3 -m src.orchestrator portfolio.txt --profiles standard

# Weekly infrastructure check
python3 -m src.orchestrator portfolio.txt --profiles dns,infrastructure

# Daily uptime monitoring
python3 -m src.orchestrator portfolio.txt --profiles monitor
```

---

## ⚙️ Configuration

### Setting Default Profiles

In `config.yaml`:

```yaml
orchestrator:
  default_profiles: [standard]  # Used when --profiles not specified
```

### Custom Profile Combinations

Create your own combos:

```yaml
# config.yaml
meta_profiles:
  my-custom-scan:
    includes:
      - dns
      - infrastructure
      - technology
    description: "Quick tech stack + hosting analysis"
```

Then use:
```bash
python3 -m src.orchestrator domains.txt --profiles my-custom-scan
```

---

## 🆘 Troubleshooting

**Q: Why is `headers` profile not returning data?**  
A: `headers` depends on `http`. You must include both:
```bash
--profiles http,headers  # ✅ Correct
--profiles headers        # ❌ Won't work
```

**Q: How do I know which profiles depend on others?**  
A: Check the profile description or `TASK_MATRIX.md`:
- 🔵 Core profiles = Independent
- 🟢 Analysis profiles = May depend on core profiles
- 🟡 Intelligence profiles = May depend on analysis profiles

**Q: Can I run just one check from a profile?**  
A: Not directly. Profiles are atomic units. But you can create a custom profile with specific checks in `config.yaml`.

**Q: Why is `clustering` not finding relationships?**  
A: `clustering` needs data from other profiles first:
```bash
# Run these first to populate data
--profiles dns,ssl,whois,technology,fingerprinting,clustering
```

**Q: Scans are slow, how do I speed up?**  
- Use fewer profiles (only what you need)
- Increase parallelism (`--workers 20`)
- Skip expensive profiles like `fingerprinting` and `compliance`

---

## 📚 Related Documentation

- **Technical Matrix:** See `TASK_MATRIX.md` for complete profile definitions
- **Check Catalog:** See `PLANNED_CHECKS.md` for all available checks  
- **Implementation:** See `LAUNCH_PLAN.md` for development roadmap
- **Configuration:** See `config.yaml` for runtime settings

---

## 🎓 Best Practices

### 1. Start Small, Build Up
```bash
# Don't jump to complete immediately
# Start with core data profiles, add as needed

--profiles dns              # Just DNS
--profiles dns,infrastructure  # Add hosting info
--profiles dns,infrastructure,technology  # Add tech stack
```

### 2. Understand Dependencies
```bash
# These work independently (core profiles):
--profiles whois
--profiles dns
--profiles http
--profiles ssl

# These need dependencies (analysis profiles):
--profiles http,headers     # headers needs http
--profiles http,content,technology  # technology needs both
```

### 3. Use Meta Profiles for Common Tasks
```bash
# Instead of remembering combinations, use meta profiles:
--profiles standard          # For general analysis
--profiles technical-audit   # For security/infrastructure
--profiles business-research # For market intelligence
```

### 4. Profile for Performance
```bash
# For 10,000 domains, use quick-check first:
--profiles quick-check

# Then only analyze the ~3,000 active ones:
--profiles standard
```

### 5. Combine for Custom Analysis
```bash
# Need DNS + business info only?
--profiles dns,whois,business

# Need security + compliance audit?
--profiles ssl,headers,security,compliance
```

---

**Remember:** Profiles are **composable**. Mix and match to create exactly the analysis you need, without wasting time on checks you don't care about. 🎯
