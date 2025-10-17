# Domain Analyzer Documentation

This project is a modular domain analysis system for researching Lithuanian (.lt) domains.  
It uses **Python + PostgreSQL** to collect, store, and analyze comprehensive domain data.

## Stack
- Python 3.9+ (async/await, aiohttp)
- PostgreSQL (database with JSONB)
- Ubuntu server (production deployment)
- (Later) FastAPI for API endpoints
- (Later) React dashboard for visualization

## Goal
Collect, store, and analyze information about Lithuanian domains efficiently using tiered scan profiles.

---

## 📚 Documentation Index

### Getting Started
- **[SETUP.md](SETUP.MD)** - Installation and environment setup
- **[CONTEXT.md](CONTEXT.md)** - Project context and background
- **[LAUNCH_PLAN.md](LAUNCH_PLAN.md)** - Version roadmap (v0.1 → v3.x)

### User Guides
- **[TASK_PROFILES.md](TASK_PROFILES.md)** - Guide to scan profiles (quick-check, basic-scan, full-scan, research-scan, monitor)

### Technical Reference
- **[TASK_MATRIX.md](TASK_MATRIX.md)** - Complete check-to-profile mapping matrix
- **[PLANNED_CHECKS.md](PLANNED_CHECKS.md)** - Catalog of all possible domain checks organized by tier

### Design Documents
- **[V08_OPTIMIZATION_DESIGN.md](V08_OPTIMIZATION_DESIGN.md)** - Check process optimization with early bailout
- **[V09_REDIRECT_CAPTURE_DESIGN.md](V09_REDIRECT_CAPTURE_DESIGN.md)** - Automatic domain discovery via redirects
- **[V10_TASK_PROFILES_DESIGN.md](V10_TASK_PROFILES_DESIGN.md)** - Task profile system architecture

---

## 🚀 Quick Start

### Run Quick Check (Filter Domains)
```bash
# Fast filtering - registration + activity
python3 -m src.orchestrator domains.txt --profiles quick-check
```

### Run Standard Analysis
```bash
# Core technical checks
python3 -m src.orchestrator active_domains.txt --profiles standard
```

### Custom Analysis
```bash
# Just DNS and SSL
python3 -m src.orchestrator domains.txt --profiles dns,ssl

# Security audit
python3 -m src.orchestrator domains.txt --profiles ssl,headers,security

# Business intelligence
python3 -m src.orchestrator domains.txt --profiles whois,business,language
```

### Query Results
```bash
# View latest results
python query_db.py latest

# View specific domain
python query_db.py domain example.com
```

---

## 📊 Profile System

**Composable Architecture**: Mix and match profiles for custom analysis

| Category | Profiles | Purpose |
|----------|----------|---------|
| **🔵 Core Data** | `whois` `dns` `http` `ssl` | Extract raw data (make API calls) |
| **🟢 Analysis** | `headers` `content` `infrastructure` `technology` `seo` | Process core data (no additional calls) |
| **🟡 Intelligence** | `security` `business` `language` `compliance` `fingerprinting` `clustering` | Business insights |
| **🟠 Meta** | `quick-check` `standard` `technical-audit` `business-research` `complete` `monitor` | Pre-configured combos |

**Examples:**
```bash
# Just DNS records
--profiles dns

# Security audit
--profiles ssl,headers,security

# Business intelligence
--profiles whois,business,language

# Everything
--profiles complete
```

See **[TASK_PROFILES.md](TASK_PROFILES.md)** for detailed guide.

---

## 🗺️ Project Status

**Current Version:** v0.6.0 (Database persistence complete)

**Implemented Checks (6):**
- ✅ WHOIS registration status (placeholder)
- ✅ Active status detection (placeholder)
- ✅ HTTP status code
- ✅ Redirect chain tracking
- ✅ SSL certificate validation
- ✅ robots.txt / sitemap.xml checks

**Planned Checks:** 114+ (see PLANNED_CHECKS.md)

**Next Milestones:**
- v0.8: Check optimization with early bailout
- v0.9: Redirect capture for domain discovery
- v0.10: Task profile system
- v1.x: Tier 1 checks (DNS, WHOIS deep dive)
- v2.x: Tier 2 checks (security, content analysis)
- v3.x: AI-powered intelligence

---

## 📖 Key Concepts

### Composable Profile System
Profiles are organized by **data source**, not scan depth:
- **Core Profiles** (`whois`, `dns`, `http`, `ssl`) - Make API calls, extract raw data
- **Analysis Profiles** (`headers`, `content`, `seo`) - Process core data without additional calls
- **Intelligence Profiles** (`security`, `business`, `language`) - Business insights and research
- **Meta Profiles** (`quick-check`, `standard`, `complete`) - Pre-configured combinations

**Why this matters:** One DNS query returns A, AAAA, MX, NS, TXT records together. Analysis profiles reuse this data without redundant calls.

### Usage Examples
```bash
# Just DNS data
--profiles dns

# DNS + hosting analysis (analysis profile reuses DNS data)
--profiles dns,infrastructure

# Security focus
--profiles ssl,headers,security

# Custom combination
--profiles whois,dns,business,language
```

### Tiered Check System
Checks are organized into 3 tiers by complexity:
- **Tier 1:** Essential status & basic connectivity (fast)
- **Tier 2:** Detailed technical, security & infrastructure (moderate)
- **Tier 3:** Content, compliance, fingerprinting & business analysis (slow)

### Early Bailout Optimization
To save resources:
1. Check registration → Skip all checks if unregistered
2. Check activity → Skip expensive checks if inactive
3. Run selected profiles → Only for active, registered domains

---

## 🔍 Finding Information

**"How do I filter 10,000 domains?"**  
→ See [TASK_PROFILES.md](TASK_PROFILES.md) - Use `--profiles quick-check`

**"What profiles are available?"**  
→ See [TASK_MATRIX.md](TASK_MATRIX.md) - 22 composable profiles

**"How do I combine profiles?"**  
→ See [TASK_PROFILES.md](TASK_PROFILES.md) - Examples: `--profiles dns,ssl`, `--profiles standard`

**"Which checks run in the dns profile?"**  
→ See [TASK_MATRIX.md](TASK_MATRIX.md) - Complete profile definitions

**"What checks are available?"**  
→ See [PLANNED_CHECKS.md](PLANNED_CHECKS.md) - 131+ checks organized by tier

**"How do I implement a new check?"**  
→ See [LAUNCH_PLAN.md](LAUNCH_PLAN.md) - Development roadmap

**"What's the architecture?"**  
→ See [V10_TASK_PROFILES_DESIGN.md](V10_TASK_PROFILES_DESIGN.md) - Composable system design

---

## 🎯 Use Cases

### Domain Portfolio Management
```bash
# Initial comprehensive scan
python3 -m src.orchestrator my_domains.txt --profiles standard

# Daily monitoring
python3 -m src.orchestrator my_domains.txt --profiles monitor
```

### Market Research
```bash
# Discover active domains
python3 -m src.orchestrator all_lt_domains.txt --profiles quick-check

# Business intelligence
python3 -m src.orchestrator active_domains.txt --profiles whois,business,language
```

### Security Audit
```bash
# Technical assessment
python3 -m src.orchestrator company_domains.txt --profiles ssl,headers,security
```

### Infrastructure Analysis
```bash
# DNS + hosting + CDN detection
python3 -m src.orchestrator domains.txt --profiles dns,infrastructure
```

---

## 🛠️ Development

**Project Structure:**
```
src/
  checks/          # Individual check modules
  core/            # Schema definitions
  utils/           # Config, logging, database
  orchestrator.py  # Main coordination
docs/              # All documentation
db/migrations/     # Database migrations
```

**Adding a New Check:**
1. Review PLANNED_CHECKS.md to find your check
2. Determine which profile it belongs to (by data source)
3. Implement check module in src/checks/
4. Update TASK_MATRIX.md status (🔄 → ✅)
5. Add check to profile definition in config.yaml
6. Test profile works independently and with dependencies
7. Document any new dependencies

---

## 📞 Support

For questions about:
- **Usage** → Read [TASK_PROFILES.md](TASK_PROFILES.md)
- **Development** → Read [LAUNCH_PLAN.md](LAUNCH_PLAN.md)
- **Architecture** → Read design docs (V08, V09, V10)
- **Setup** → Read [SETUP.md](SETUP.MD)

---

**Last Updated:** October 14, 2025  
**Documentation Version:** 1.0
