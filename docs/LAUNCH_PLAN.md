# LAUNCH_PLAN.md — Incremental Releases

This roadmap defines **sequential, non-breaking launches** for the Domain Analyzer project.  
Each launch ends in a working version, tagged in Git (e.g. `v0.3`, `v1.0`, `v2.0`, ...).  
After completing each step, commit, test, and tag before moving forward.

---

# 🚀 FUTURE VERSIONS — MVP & Beyond

**Strategy:**
- **v1.x** = Core Data Profiles (MVP with 4 essential profiles)
- **v2.x** = Frontend Dashboard (from minimal to full-featured)
- **v3.x** = Analysis Profiles (processing core data)
- **v4.x** = Intelligence Profiles (business insights & AI)
- **v5.x+** = Advanced Features (clustering, monitoring, APIs)

---

## ✅ COMPLETED: PHASE 1: Core Data Profiles (MVP)

These versions complete the **Core Data** layer - the foundation that makes external API calls.

---

## ✅ COMPLETED: Version 1.1 — WHOIS Profile

### 🎯 Goal
Add detailed WHOIS data retrieval using dual protocol approach (DAS + WHOIS port 43).

### 📋 Strategy
**Dual Protocol Approach:**
1. **DAS (port 4343)** - Fast registration status checking (existing, keep it)
2. **WHOIS (port 43)** - Detailed data for registered domains only (new)

This maintains fast bulk scanning while getting detailed data where needed.

### 📋 Tasks
1. **Implement WHOISClient class** in `checks/whois_check.py`:
   - ✅ Add standard WHOIS protocol client (port 43)
   - ✅ Parse .lt WHOIS response format
   - ✅ Extract: registrar, registration date, expiration date, nameservers
   - ✅ Rate limiting: 100 queries per 30 minutes (token bucket)
   
2. **Integrate dual protocol flow**:
   - ✅ DAS check first (already working from v0.8) - fast filtering
   - ✅ NEW: WHOIS query for registered domains only
   - ✅ Graceful degradation if rate limited (return DAS-only data)
   
3. **Data extraction** from WHOIS response:
   - ✅ Registrar name (no need to save contact)
   - ✅ Registration date
   - ✅ Expiration date  
   - ✅ Nameservers
   - ✅ Domain age calculation (from registration date)
   - ✅ Privacy protection detection (when registrant data absent)

4. **Update `whois` profile** in `config.yaml`:
   - ✅ Mark WHOIS checks as implemented
   - ✅ Add WHOIS rate limit configuration

### 🧪 Validation
- ✅ `--profiles whois` returns complete registration data for registered domains
- ✅ Correctly parses: registrar, dates, nameservers
- ✅ Domain age calculated accurately
- ✅ Rate limiting prevents IP blocking
- ✅ Handles rate limit gracefully (returns partial data)
- ✅ Fast bulk scanning maintained (DAS for unregistered)

### 📦 Tag
```bash
git commit -m "v1.1 - dual protocol WHOIS implementation (DAS + port 43)"
git tag v1.1
```

---

## 🟣 Version 1.2 — Quick HTTP Profile (Bulk Scan Optimization)

### 🎯 Goal
Enable ultra-fast bulk scanning of 150k+ domains by splitting HTTP checks into quick and detailed variants. This mirrors the successful `quick-whois` pattern from v1.1.1, optimizing the two-phase scanning workflow:
1. **Phase 1**: `quick-check` (quick-whois + quick-http) → Filter to registered + active domains
2. **Phase 2**: Detailed profiles on filtered subset → Much smaller dataset, can afford slower checks

### 📋 Strategy
**Split HTTP checks by purpose:**
- **`quick-http` profile**: HTTP HEAD requests only, 2s timeout, fast filtering (is domain active?)
- **`http` profile**: Full GET requests, 10s timeout, complete analysis (redirects, content, headers)

**Performance Impact:**
- Current `quick-check`: ~10-30s per domain (GET requests with 10s timeout)
- New `quick-check`: ~0.5-2s per domain (HEAD requests with 2s timeout)
- **For 150k domains**: ~40 hours → **2-4 hours** (10-20x faster!)

### 📋 Tasks

#### 1. Create `quick-http` profile
**File**: `src/checks/quick_http_check.py` (new file)

**Implementation:**
- HTTP HEAD request only (no body download)
- 2-second aggressive timeout (fail-fast for dead domains)
- HTTPS first, fallback to HTTP
- Connection pooling and DNS caching
- Early exit on first successful response

**Returns minimal viable data:**
```python
{
    "status": "active",           # or "inactive"
    "http_status": 200,           # HTTP status code
    "protocol": "https",          # which protocol worked
    "final_url": "https://www.example.lt",  # after redirects
    "redirect_count": 1,          # number of redirects
    "response_time_ms": 150       # response time
}
```

**Configuration** (`config.yaml`):
```yaml
checks:
  quick-http:
    enabled: true
    timeout: 2.0              # Aggressive 2-second timeout
    connect_timeout: 1.0      # 1 second to establish connection
    sock_read_timeout: 0.5    # 0.5 seconds to read headers
    max_redirects: 5          # Limit redirect chains
    protocols: ['https', 'http']  # Try HTTPS first
```

#### 2. Update database schema
**File**: `db/schema.sql`

**Add tracking columns to `domains` table:**
```sql
-- Activity tracking (similar to is_registered from v1.1)
ALTER TABLE domains ADD COLUMN is_active_source VARCHAR(50);
ALTER TABLE domains ADD COLUMN is_active_updated_at TIMESTAMP;

-- Index for fast filtering
CREATE INDEX idx_domains_is_active ON domains(is_active);
CREATE INDEX idx_domains_active_registered ON domains(is_active, is_registered);
```

**Purpose:**
- `is_active`: Boolean flag set by `quick-http` (already exists)
- `is_active_source`: Track which check set the flag ('quick-http', 'http', 'manual')
- `is_active_updated_at`: Timestamp for activity verification age

**Update `domain_results` JSONB schema:**
- Add `quick-http` check data structure
- Store HEAD request results separately from GET request results

#### 3. Update full `http` profile
**File**: `src/checks/http_check.py` (existing file)

**Changes:**
- Switch from HEAD to **GET requests** for complete analysis
- Keep 10-second timeout for detailed checks
- Add content analysis (size, compression, etc.)
- Expand redirect chain tracking
- Add performance metrics

**Enhanced data returned:**
```python
{
    "status": "active",
    "http_status": 200,
    "protocol": "https",
    "final_url": "https://www.example.lt",
    "redirect_count": 1,
    "redirect_chain": [...],     # Full redirect history
    "response_time_ms": 350,
    "content_length": 45231,     # Body size
    "compression": "gzip",       # Compression type
    "server": "nginx/1.18.0",    # Server header
    "http_version": "HTTP/2",    # Protocol version
    "ttfb_ms": 120,             # Time to first byte
}
```

#### 4. Update profile system
**File**: `src/profiles/profile_schema.py`

**Add `quick-http` to core profiles:**
```python
PROFILE_DEPENDENCIES = {
    # Core profiles (make external API calls)
    'quick-http': [],  # New: Fast HTTP HEAD check
    'http': [],        # Updated: Full HTTP GET analysis
    
    # Meta profiles (expand to other profiles)
    'quick-check': ['quick-whois', 'quick-http'],  # Updated
    'standard': ['whois', 'dns', 'http', 'ssl', 'seo'],  # Uses full http
}

PROFILE_METADATA = {
    'quick-http': {
        'category': ProfileCategory.CORE,
        'description': 'Fast HTTP connectivity check (HEAD request only)',
        'data_source': 'HTTP/HTTPS HEAD requests',
        'api_calls': 2,  # HTTPS + HTTP fallback
        'duration_estimate': '0.5-2s',
        'rate_limit': None,
        'use_cases': [
            'Bulk domain filtering',
            'Active/inactive classification',
            'Quick connectivity verification'
        ],
    },
    'http': {
        'category': ProfileCategory.CORE,
        'description': 'Complete HTTP analysis with content inspection',
        'data_source': 'HTTP/HTTPS GET requests',
        'api_calls': 2,
        'duration_estimate': '2-10s',
        'rate_limit': None,
        'use_cases': [
            'Detailed redirect analysis',
            'Performance metrics',
            'Content and header inspection'
        ],
    },
}
```

#### 5. Enable early bailout optimization
**File**: `src/orchestrator.py`

**Add inactive domain filtering:**
```python
def determine_checks_to_run(self, domain_obj, profiles):
    """Determine which checks to run based on domain state."""
    
    # Early bailout: unregistered domains (v1.1)
    if not domain_obj.is_registered:
        return ['whois']  # Only try registration check
    
    # Early bailout: inactive domains (v1.2 NEW)
    if not domain_obj.is_active and self.requires_active_site(profiles):
        return []  # Skip content-based checks
    
    # Full check suite
    return self.expand_profiles(profiles)

def requires_active_site(self, profiles):
    """Check if profiles require active website."""
    content_profiles = ['seo', 'content', 'headers', 'robots', 'sitemap']
    return any(p in content_profiles for p in profiles)
```

**Benefits:**
- Unregistered domains: Skip all checks (v1.1)
- Inactive domains: Skip content checks (v1.2)
- Massive time savings on large datasets

#### 6. Configuration updates
**File**: `config.yaml`

**Add profile-specific settings:**
```yaml
# Network configuration with profile overrides
network:
  default_timeout: 10
  request_timeout: 10  # Default for full http profile
  
profiles:
  quick-http:
    enabled: true
    checks:
      - connectivity_status  # HEAD request only
      
  http:
    enabled: true
    checks:
      - connectivity_status  # GET request with full analysis
      - redirect_chain
      - performance_metrics
      - content_analysis
```

### 🧪 Validation Criteria

**Quick-HTTP Profile:**
- `--profiles quick-http` completes in <2s per domain
- Sets `is_active` flag correctly (true/false)
- Returns minimal data (status, protocol, http_status, final_url)
- Fails fast on dead domains (2s timeout)
- Tracks data source in `is_active_source`

**Full HTTP Profile:**
- `--profiles http` uses GET requests (not HEAD)
- Returns complete analysis data
- Handles 10s timeout for slow servers
- Can override `is_active` if quick-http had false negative

**Quick-Check Meta Profile:**
- `--profiles quick-check` runs both `quick-whois` + `quick-http`
- Completes in ~2-3s per domain (both checks combined)
- Sets both `is_registered` and `is_active` flags
- Enables early bailout for subsequent profiles

**Orchestrator Early Bailout:**
- Inactive domains skip content-based checks
- Manual override capability (set `is_active_source='manual'`)
- Proper filtering in database queries

**Performance Benchmarks:**
- 150k domains with `quick-check`: <4 hours (vs ~40 hours previously)
- 80k filtered active domains with `standard`: ~10-15 hours
- Total two-phase scan: <20 hours (vs >60 hours single-phase)

### 📦 Migration Notes

**Database migration:**
```sql
-- Add new columns
ALTER TABLE domains 
  ADD COLUMN is_active_source VARCHAR(50),
  ADD COLUMN is_active_updated_at TIMESTAMP;

-- Create indexes
CREATE INDEX idx_domains_is_active ON domains(is_active);
CREATE INDEX idx_domains_active_registered ON domains(is_active, is_registered);

-- Backfill existing data (set source for existing is_active flags)
UPDATE domains 
SET is_active_source = 'legacy',
    is_active_updated_at = updated_at
WHERE is_active IS NOT NULL;
```

### 📦 Tag
```bash
git commit -m "v1.2 - quick-http profile for bulk scan optimization"
git tag v1.2
```

### 📄 Future Enhancements (Post-v1.2)

**Potential improvements:**
- TCP port pre-check (80/443 open before HTTP request)
- Parallel protocol checking (HTTP + HTTPS simultaneously)
- Response caching for repeated checks
- Adaptive timeout based on historical performance
- Manual domain re-verification workflow

---

## 🟣 Version 1.3 — DNS Profile

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
git commit -m "v1.3 - complete DNS profile implementation"
git tag v1.3
```

---

## 🟣 Version 1.4 — SSL Profile

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
   - Parallel execution of all core profiles (5 in v1.1.1: quick-whois, whois, dns, http, ssl)
   - Connection pooling for HTTP requests
   - DNS query caching (TTL-aware)
   - Retry logic with exponential backoff

2. Error handling improvements:
   - Graceful degradation (partial results if some checks fail)
   - Detailed error messages in results
   - Rate limit detection and handling

3. Add core meta profiles:
   - `quick-check` - quick-whois + active detection (v1.1.1: uses fast DAS protocol)
   - `standard` - Core profiles (whois, dns, http, ssl)
   - `monitor` - Lightweight recurring checks (quick-whois + http)

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
- All core profiles (5 in v1.1.1) working independently and in combination
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

## 🟣 Version 3.4 — SEO Profile

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

### WHOIS Data Enrichment (Advanced)
- **Detect registrar transfers** - Compare WHOIS history to identify domain ownership changes
- **Flag expiring domains** - Alert when domains expire in < 30 days
- **Identify high-risk registrars** - Flag domains registered with known problematic registrars
- **WHOIS history tracking** - Store and compare historical WHOIS data

### Scaling & Distribution
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
