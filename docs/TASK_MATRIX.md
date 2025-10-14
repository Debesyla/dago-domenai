# Task Profile Matrix

This document defines the **composable profile system** where profiles are organized by data source and check type, not by scan depth. Users can combine multiple profiles to create custom scanning strategies.

---

## 🎯 Architecture Philosophy

### Key Principle: Organize by Data Source, Not Scan Depth

**Traditional Approach (❌ Inefficient):**
```
basic-scan: whois + dns + http (makes 3 separate API calls)
full-scan: whois + dns + http AGAIN (redundant calls)
```

**Our Approach (✅ Efficient):**
```
whois profile: ONE API call → all WHOIS data
dns profile: ONE query set → all DNS records
http profile: ONE request → all HTTP data

Users combine: --profiles whois,dns,http
```

### Benefits
1. **Performance** - Each data source queried once, all related checks extracted
2. **Flexibility** - Users compose profiles for their exact needs
3. **Maintainability** - Adding checks to existing profile doesn't break others
4. **Natural** - Mirrors actual implementation (one DNS query returns A, AAAA, MX, TXT together)

---

## 📊 Profile Categories

### 🔵 Core Data Retrieval Profiles
Extract raw data from external sources (WHOIS servers, DNS, HTTP, SSL handshakes)

### 🟢 Analysis Profiles
Process data from core profiles (analyze headers, parse content, detect tech stack)

### 🟡 Intelligence Profiles
Business and research insights (compliance, SEO, language, clustering)

### 🟠 Meta Profiles
Pre-configured combinations for common use cases (quick-check, standard, complete)

---

## � Complete Profile Definitions

### Legend
- ✅ **Implemented** - Check is working in current version
- 🔄 **Planned** - Check will be added in specified version
- 🔗 **Depends On** - Profile requires data from another profile

---

## 🔵 Core Data Retrieval Profiles

These profiles make external API calls to retrieve raw data.

---

### Profile: `whois`
**Purpose:** Registration and ownership information  
**Data Source:** WHOIS servers / RDAP API  
**API Calls:** 1 WHOIS query per domain  
**Duration:** 0.5-1 second

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| WHOIS registration status | ✅ | v0.6 | 🟢 |
| Registrar name and IANA ID | 🔄 | v0.8.1 | 🟢 |
| Registrant organization | 🔄 | v1.3 | 🟢 |
| Registration date | 🔄 | v0.8.1 | 🟢 |
| Expiration date | 🔄 | v0.8.1 | 🟢 |
| Updated date | 🔄 | v1.3 | 🟢 |
| Registry status codes | 🔄 | v1.3 | 🟢 |
| Privacy protection enabled | 🔄 | v1.3 | 🟢 |
| Domain age (calculated) | 🔄 | v1.3 | 🟡 |
| Detect registrar transfers | 🔄 | v2.1 | 🟡 |

**Total Checks:** 10 (1 implemented, 9 planned)

---

### Profile: `dns`
**Purpose:** DNS resolution and all record types  
**Data Source:** DNS servers  
**API Calls:** 1 query set (A, AAAA, MX, NS, TXT, CNAME in parallel)  
**Duration:** 0.3-0.8 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| A record (IPv4) | 🔄 | v1.1 | 🟢 |
| AAAA record (IPv6) | 🔄 | v1.1 | 🟢 |
| MX records (mail servers) | 🔄 | v1.2 | 🟢 |
| NS records (nameservers) | 🔄 | v1.1 | 🟢 |
| TXT records (SPF, DKIM, DMARC) | 🔄 | v1.2 | 🟢 |
| CNAME records | 🔄 | v1.2 | 🟢 |
| DNSSEC enabled | 🔄 | v2.1 | 🟡 |
| Reverse DNS (PTR) | 🔄 | v2.1 | 🟡 |
| Invalid private IP resolution | 🔄 | v2.1 | 🟡 |
| Wildcard DNS detection | 🔄 | v2.2 | 🟡 |
| Zone propagation check | 🔄 | v3.0 | 🟡 |

**Total Checks:** 11 (0 implemented, 11 planned)

---

### Profile: `http`
**Purpose:** HTTP connectivity, redirects, and response behavior  
**Data Source:** HTTP/HTTPS requests  
**API Calls:** 1-2 HTTP requests (HTTP + HTTPS)  
**Duration:** 1-3 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| HTTP status code | ✅ | v0.4 | 🟢 |
| Final redirect destination | ✅ | v0.5 | 🟢 |
| Redirect chain tracking | ✅ | v0.5 | 🟢 |
| Response time | 🔄 | v1.1 | 🟢 |
| HTTPS availability | 🔄 | v1.1 | 🟢 |
| HTTP to HTTPS redirect | 🔄 | v1.1 | 🟢 |
| Time to first byte (TTFB) | 🔄 | v1.3 | 🟡 |
| Detect redirect loops | 🔄 | v1.2 | 🟡 |
| HTTP/2 or HTTP/3 support | 🔄 | v2.1 | 🟡 |
| Compression detection (Gzip/Brotli) | 🔄 | v2.1 | 🟡 |

**Total Checks:** 10 (3 implemented, 7 planned)

---

### Profile: `ssl`
**Purpose:** SSL/TLS certificate analysis  
**Data Source:** TLS handshake  
**API Calls:** 1 SSL connection  
**Duration:** 0.5-1.5 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| SSL certificate presence | ✅ | v0.5 | 🟢 |
| SSL certificate expiration | ✅ | v0.5 | 🟢 |
| SSL issuer (CA) | ✅ | v0.5 | 🟢 |
| SSL validation type (DV/OV/EV) | 🔄 | v1.1 | 🟡 |
| Certificate chain validity | 🔄 | v1.1 | 🟡 |
| Certificate subject details | 🔄 | v1.3 | 🟢 |
| SSL/TLS protocol version | 🔄 | v2.1 | 🟡 |
| Cipher suite information | 🔄 | v2.1 | 🟡 |

**Total Checks:** 8 (3 implemented, 5 planned)

---

## 🟢 Analysis Profiles

These profiles process data from core profiles without making additional external calls.

---

### Profile: `headers`
**Purpose:** HTTP header analysis for security and configuration  
**Depends On:** 🔗 `http` profile  
**Additional Calls:** 0 (uses http response data)  
**Duration:** < 0.1 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Response headers snapshot | 🔄 | v1.1 | 🟢 |
| HSTS header presence | 🔄 | v1.2 | 🟢 |
| X-Content-Type-Options | 🔄 | v1.2 | 🟢 |
| Referrer-Policy | 🔄 | v1.2 | 🟢 |
| Content-Security-Policy (CSP) | 🔄 | v2.1 | 🟡 |
| Permissions-Policy | 🔄 | v2.1 | 🟡 |
| HSTS max-age and includeSubDomains | 🔄 | v2.1 | 🟡 |
| Server software detection | 🔄 | v1.2 | 🟡 |
| X-Frame-Options | 🔄 | v2.1 | 🟢 |

**Total Checks:** 9 (0 implemented, 9 planned)

---

### Profile: `content`
**Purpose:** On-page content extraction and analysis  
**Depends On:** 🔗 `http` profile  
**Additional Calls:** 0 (parses http response HTML)  
**Duration:** 0.2-0.5 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| HTML title content | 🔄 | v1.2 | 🟢 |
| Meta description tag | 🔄 | v1.2 | 🟢 |
| Content language meta | 🔄 | v1.2 | 🟢 |
| Charset encoding | 🔄 | v1.2 | 🟢 |
| Canonical URL tag | 🔄 | v1.2 | 🟢 |
| Meta robots (noindex/nofollow) | 🔄 | v1.2 | 🟢 |
| Page size (bytes) | 🔄 | v1.2 | 🟢 |
| HTML to text ratio | 🔄 | v2.1 | 🟢 |
| Image count and media weight | 🔄 | v2.1 | 🟡 |
| External links extraction | 🔄 | v2.1 | 🟢 |
| Detect unminified assets | 🔄 | v2.2 | 🟡 |
| JavaScript heavy site detection | 🔄 | v2.2 | 🟡 |

**Total Checks:** 12 (0 implemented, 12 planned)

---

### Profile: `infrastructure`
**Purpose:** Hosting and network infrastructure analysis  
**Depends On:** 🔗 `dns`, `http` profiles  
**Additional Calls:** 1-2 (GeoIP lookup, ASN lookup)  
**Duration:** 0.5-1 second

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| IP geolocation (country/region) | 🔄 | v1.1 | 🟢 |
| Hosting provider (ASN lookup) | 🔄 | v1.2 | 🟡 |
| Cloud hosting detection | 🔄 | v1.2 | 🟡 |
| CDN usage detection | 🔄 | v1.2 | 🟡 |
| Load balancer detection | 🔄 | v2.1 | 🟡 |
| Multiple IPs / failover setup | 🔄 | v2.1 | 🟡 |
| Foreign hosting detection | 🔄 | v2.1 | 🟡 |
| Non-standard ports open | 🔄 | v2.2 | 🟡 |

**Total Checks:** 8 (0 implemented, 8 planned)

---

### Profile: `technology`
**Purpose:** CMS, framework, and technology stack detection  
**Depends On:** 🔗 `http`, `content` profiles  
**Additional Calls:** 0 (analyzes HTML, headers, scripts)  
**Duration:** 0.2-0.5 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| CMS detection (WordPress, Drupal, etc.) | 🔄 | v1.3 | 🟡 |
| Technology stack fingerprinting | 🔄 | v1.3 | 🟡 |
| JavaScript framework detection | 🔄 | v2.1 | 🟡 |
| Analytics tags (GA, Meta, etc.) | 🔄 | v2.1 | 🟡 |
| SPA / lazy loading detection | 🔄 | v2.1 | 🟡 |
| AMP pages detection | 🔄 | v2.2 | 🟡 |
| Site generator detection | 🔄 | v2.2 | 🟡 |
| Outdated CMS version | 🔄 | v2.2 | 🟡 |

**Total Checks:** 8 (0 implemented, 8 planned)

---

## 🟡 Intelligence Profiles

These profiles provide business insights and specialized analysis.

---

### Profile: `seo`
**Purpose:** SEO-related checks and optimization analysis  
**Depends On:** 🔗 `http`, `content` profiles  
**Additional Calls:** 2 (robots.txt, sitemap.xml)  
**Duration:** 1-2 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| robots.txt existence | ✅ | v0.5 | 🟢 |
| sitemap.xml existence | ✅ | v0.5 | � |
| Favicon presence | 🔄 | v1.2 | 🟢 |
| Structured data (schema.org) | 🔄 | v2.1 | 🟡 |
| URL slug cleanliness | 🔄 | v2.1 | 🟢 |
| Crawl depth audit | 🔄 | v2.2 | 🟡 |
| Orphaned pages detection | 🔄 | v2.3 | 🟡 |
| Thin content detection | 🔄 | v2.3 | 🟡 |
| Indexed in Google | 🔄 | v2.2 | 🟡 |
| Web archive presence | 🔄 | v2.1 | 🟡 |

**Total Checks:** 10 (2 implemented, 8 planned)

---

### Profile: `security`
**Purpose:** Security vulnerability and risk assessment  
**Depends On:** 🔗 `http`, `headers`, `ssl`, `technology` profiles  
**Additional Calls:** 3-5 (check for exposed files, blacklist queries)  
**Duration:** 2-5 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| HTTP header misconfigurations | 🔄 | v2.1 | 🟡 |
| Exposed .git or .env files | 🔄 | v2.1 | 🟡 |
| Blacklist presence (DNSBL) | 🔄 | v2.2 | 🟡 |
| Phishing / malware flags | 🔄 | v2.2 | 🟡 |
| VPN / proxy IP detection | 🔄 | v2.2 | 🟡 |
| Weak SSL configuration | 🔄 | v2.2 | 🟡 |

**Total Checks:** 6 (0 implemented, 6 planned)

---

### Profile: `compliance`
**Purpose:** GDPR, privacy, and regulatory compliance  
**Depends On:** 🔗 `http`, `content` profiles (requires JS execution)  
**Additional Calls:** 0 (but needs headless browser)  
**Duration:** 3-5 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Cookie banner detection | 🔄 | v2.2 | 🟡 |
| GDPR compliance signals | 🔄 | v2.2 | 🟡 |
| Cookie consent mechanism | 🔄 | v2.2 | 🟡 |
| Privacy policy link | 🔄 | v2.2 | 🟡 |
| Terms of service link | 🔄 | v2.3 | 🟡 |

**Total Checks:** 5 (0 implemented, 5 planned)

---

### Profile: `business`
**Purpose:** Business intelligence and contact information  
**Depends On:** 🔗 `http`, `content` profiles  
**Additional Calls:** 0 (extracts from HTML)  
**Duration:** 0.3-0.8 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Social media links | 🔄 | v2.1 | 🟡 |
| Contact info extraction | 🔄 | v2.2 | 🟡 |
| Company code / VAT number | 🔄 | v2.3 | 🟡 |
| Lithuanian city mentions | 🔄 | v2.3 | 🟡 |
| Currency usage detection | 🔄 | v2.2 | 🟡 |
| Social proof elements | 🔄 | v2.3 | 🟡 |
| AI chatbot presence | 🔄 | v2.2 | 🟡 |

**Total Checks:** 7 (0 implemented, 7 planned)

---

### Profile: `language`
**Purpose:** Language detection and audience targeting  
**Depends On:** 🔗 `content` profile  
**Additional Calls:** 0 (NLP analysis on HTML text)  
**Duration:** 0.5-1 second

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Language detection | 🔄 | v2.2 | 🟡 |
| Lithuanian audience targeting | 🔄 | v2.3 | 🟡 |
| Multilingual setup detection | 🔄 | v2.2 | 🟡 |
| Language variants (hreflang) | 🔄 | v2.2 | 🟡 |
| Language mismatch detection | 🔄 | v2.2 | 🟡 |
| Lithuanian vs English ratio | 🔄 | v2.3 | 🟡 |
| Keyword extraction | 🔄 | v2.2 | 🟡 |
| Topic extraction | 🔄 | v2.2 | 🟡 |

**Total Checks:** 8 (0 implemented, 8 planned)

---

### Profile: `fingerprinting`
**Purpose:** Digital fingerprinting and visual analysis  
**Depends On:** 🔗 `http` profile (+ headless browser for screenshots)  
**Additional Calls:** 1-2 (screenshot capture, favicon download)  
**Duration:** 5-10 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Screenshot capture | 🔄 | v2.1 | 🟡 |
| Homepage HTML hash | 🔄 | v1.3 | 🟢 |
| Favicon hash | 🔄 | v1.3 | 🟢 |
| Parked domain detection | 🔄 | v2.2 | 🟡 |
| For-sale banner detection | 🔄 | v2.2 | 🟡 |

**Total Checks:** 5 (0 implemented, 5 planned)

---

### Profile: `clustering`
**Purpose:** Portfolio and relationship detection  
**Depends On:** � `dns`, `ssl`, `whois`, `technology`, `fingerprinting` profiles  
**Additional Calls:** 0 (database queries for pattern matching)  
**Duration:** 0.1-0.3 seconds

| Check | Status | Version | Difficulty |
|-------|--------|---------|------------|
| Shared IP detection | 🔄 | v2.3 | 🟡 |
| Shared analytics ID | 🔄 | v2.3 | 🟡 |
| SSL organization grouping | 🔄 | v2.3 | 🟡 |
| Shared hosting cluster | 🔄 | v2.3 | 🟡 |
| Favicon-based clustering | 🔄 | v2.3 | 🟡 |
| CSS/JS library similarity | 🔄 | v2.3 | 🟡 |

**Total Checks:** 6 (0 implemented, 6 planned)

---

## 🟠 Meta Profiles

Pre-configured combinations for common use cases.

---

### Profile: `quick-check`
**Purpose:** Fast filtering for bulk domain lists  
**Composition:** `whois` + active detection  
**Duration:** 1-2 seconds  
**Use Case:** Filter 10,000 domains down to active ones

```yaml
quick-check:
  includes:
    - whois  # Registration status
  checks:
    - active_status  # Custom check: determines if site is active
```

---

### Profile: `standard`
**Purpose:** Standard technical analysis  
**Composition:** Core data + SEO basics  
**Duration:** 5-10 seconds  
**Use Case:** General domain health check

```yaml
standard:
  includes:
    - whois
    - dns
    - http
    - ssl
    - seo
```

---

### Profile: `technical-audit`
**Purpose:** Complete technical assessment  
**Composition:** All technical profiles  
**Duration:** 15-30 seconds  
**Use Case:** Security and infrastructure analysis

```yaml
technical-audit:
  includes:
    - whois
    - dns
    - http
    - ssl
    - headers
    - infrastructure
    - technology
    - security
```

---

### Profile: `business-research`
**Purpose:** Business intelligence gathering  
**Composition:** Technical + business profiles  
**Duration:** 30-60 seconds  
**Use Case:** Market research and competitor analysis

```yaml
business-research:
  includes:
    - whois
    - dns
    - http
    - ssl
    - content
    - business
    - language
    - compliance
    - technology
```

---

### Profile: `complete`
**Purpose:** Everything available  
**Composition:** All profiles  
**Duration:** 60-120 seconds  
**Use Case:** Deep domain intelligence

```yaml
complete:
  includes: [all]
```

---

### Profile: `monitor`
**Purpose:** Lightweight recurring checks  
**Composition:** Minimal change detection  
**Duration:** 2-3 seconds  
**Use Case:** Track changes over time

```yaml
monitor:
  includes:
    - http  # Status changes
    - ssl   # Certificate changes
  checks:
    - dns_a_record  # IP changes
    - html_hash     # Content changes
```

---

## 🚀 Implementation Strategy

### Phase 1: Core Data Profiles (v0.x - v1.1)
1. ✅ `http` - Basic connectivity (v0.4-v0.5)
2. ✅ `ssl` - Certificate checks (v0.5)
3. ✅ `whois` - Registration (placeholder v0.6, full v0.8.1)
4. 🔄 `dns` - Complete DNS resolution (v1.1)

### Phase 2: Analysis Profiles (v1.2 - v1.3)
5. `headers` - Security headers
6. `content` - On-page content
7. `seo` - SEO optimization
8. `infrastructure` - Hosting analysis
9. `technology` - Tech stack detection

### Phase 3: Intelligence Profiles (v2.x)
10. `security` - Vulnerability assessment
11. `business` - Contact and company info
12. `language` - Language and targeting
13. `compliance` - GDPR and privacy
14. `fingerprinting` - Visual analysis

### Phase 4: Advanced Profiles (v2.3+)
15. `clustering` - Portfolio detection
16. AI-powered profiles (v3.x)

---

## 📊 Summary Statistics

| Category | Profiles | Total Checks | Implemented | Planned |
|----------|----------|--------------|-------------|---------|
| **Core Data** | 4 | 39 | 7 | 32 |
| **Analysis** | 5 | 45 | 0 | 45 |
| **Intelligence** | 7 | 47 | 2 | 45 |
| **Meta** | 6 | - | - | - |
| **TOTAL** | 22 | 131 | 9 | 122 |

---

## � Usage Examples

### Example 1: Quick Filtering
```bash
# Just check registration and activity
python -m src.orchestrator domains.txt --profiles quick-check
```

### Example 2: DNS Analysis Only
```bash
# Get all DNS records
python -m src.orchestrator domains.txt --profiles dns
```

### Example 3: Security Audit
```bash
# SSL + headers + security vulnerabilities
python -m src.orchestrator domains.txt --profiles ssl,headers,security
```

### Example 4: Custom Combination
```bash
# Infrastructure + technology stack
python -m src.orchestrator domains.txt --profiles dns,infrastructure,technology
```

### Example 5: Business Intelligence
```bash
# Company info + language + compliance
python -m src.orchestrator domains.txt --profiles whois,business,language,compliance
```

### Example 6: Complete Analysis
```bash
# Everything
python -m src.orchestrator domains.txt --profiles complete
```

---

## 🔄 Adding New Checks

When implementing a new check:

1. **Identify the data source** - Does it need a new API call?
2. **Choose the right profile** - Which profile should contain it?
3. **Check dependencies** - Does it depend on data from other profiles?
4. **Update this matrix** - Change 🔄 to ✅ and add version number
5. **Update config.yaml** - Add check to profile definition
6. **Test in isolation** - Verify profile works independently
7. **Test in combination** - Verify it works with dependent profiles

---

## 📝 Notes

- **Dependency Management:** Some profiles depend on others (e.g., `headers` needs `http` data). The orchestrator must run dependencies first.
- **Data Reuse:** When multiple profiles need the same data (e.g., both `content` and `technology` need HTML), fetch it once and share.
- **Caching:** Results from core data profiles can be cached for a short time to enable rapid re-analysis with different intelligence profiles.
- **Parallel Execution:** Core data profiles (whois, dns, http, ssl) can run in parallel. Analysis profiles run after their dependencies complete.
