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

### 🚀 Getting Started
- **[README.md](README.md)** (this file) - Project overview and quick start
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete production deployment guide

### 📖 User Guides  
- **[TASK_PROFILES.md](TASK_PROFILES.md)** - Comprehensive guide to scan profiles (quick-whois, quick-check, standard, complete, etc.)
- **[PROFILE_QUICK_REFERENCE.md](PROFILE_QUICK_REFERENCE.md)** - Quick reference card for profiles

### 🔧 Technical Reference
- **[TASK_MATRIX.md](TASK_MATRIX.md)** - Complete check-to-profile mapping matrix
- **[PLANNED_CHECKS.md](PLANNED_CHECKS.md)** - Catalog of all domain checks organized by profile

### 🗺️ Project Roadmap
- **[LAUNCH_PLAN.md](LAUNCH_PLAN.md)** - Version roadmap and feature timeline

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

**Current Version:** v1.1.1 (Quick-WHOIS profile split)

**Implemented Features:**
- ✅ Composable profile system (v0.10)
- ✅ Early bailout optimization (v0.8)
- ✅ Domain discovery via redirects (v0.9)
- ✅ Dual WHOIS protocol support (v1.1)
  - DAS protocol: Fast bulk checking (4 queries/sec)
  - WHOIS port 43: Detailed registration data (rate limited)
- ✅ Profile-aware check orchestration
- ✅ PostgreSQL persistence with JSONB
- ✅ Async/await architecture

**Implemented Checks (7):**
- ✅ Quick-WHOIS (DAS-only, fast registration check)
- ✅ WHOIS (full registration data with contacts)
- ✅ HTTP status and redirects
- ✅ SSL certificate validation
- ✅ robots.txt / sitemap.xml checks
- ✅ Active status detection
- ✅ Redirect chain tracking

**Next Milestones:**
- v1.2: DNS deep dive checks
- v1.3: SEO analysis profiles  
- v2.x: Security and content analysis
- v3.x: AI-powered intelligence

See **[LAUNCH_PLAN.md](LAUNCH_PLAN.md)** for full roadmap.

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
```bash
# Just DNS data
--profiles dns

# DNS + hosting analysis (analysis profile reuses DNS data)
--profiles dns,infrastructure

# Security focus
--profiles ssl,headers,security

# Custom combination
--profiles dns,http,ssl,seo
```

### Early Bailout Optimization
DAGO automatically skips unregistered/inactive domains to save time:
- **WHOIS check first**: If unregistered → skip all other checks
- **HTTP check second**: If inactive → skip analysis checks
- **Profile-aware**: Each profile defines which early bailout checks to run

---

## 🛠️ Local Development Setup

### Prerequisites
- **Python 3.9+**
- **PostgreSQL 12+**
- **Git**

### Quick Setup

```bash
# Clone repository
git clone https://github.com/Debesyla/dago-domenai.git
cd dago-domenai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.app.txt

# Set up database
./db/setup.sh
# Or manually:
# createdb domenai
# psql domenai -f db/schema.sql

# Configure
cp config.yaml config.local.yaml
# Edit config.local.yaml with your database credentials

# Run tests
pytest tests/unit/ -v

# Test a scan
python -m src.orchestrator --domain debesyla.lt --profiles quick-whois
```

### Development Tips

**Running specific profiles:**
```bash
# Test quick-whois (fast, ~0.02s)
python -m src.orchestrator --domain example.lt --profiles quick-whois

# Test full whois (detailed, ~0.10s)  
python -m src.orchestrator --domain example.lt --profiles whois

# Test DNS resolution
python -m src.orchestrator --domain example.lt --profiles dns
```

**Database queries:**
```bash
# Check scan results
psql domenai -c "SELECT domain_name, is_registered, is_active FROM domains LIMIT 10;"

# View profile usage
psql domenai -c "SELECT name, profiles FROM tasks WHERE is_meta_profile = TRUE;"
```

**Monitoring scans:**
```bash
# Start background scan
nohup python -m src.orchestrator domains.txt --profiles quick-check > logs/scan.log 2>&1 &

# Monitor progress
./monitor_scan.sh
```

For **production deployment**, see **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**.

---
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
  checks/            # Individual check modules (whois, dns, http, ssl, etc.)
  core/              # Schema definitions
  profiles/          # Profile system (loader, schema)
  utils/             # Config, logging, database, export
  orchestrator.py    # Main coordination engine
docs/                # All documentation
db/                  # Database schema and setup
tests/               # Unit and integration tests
```

**Adding a New Check:**
1. Review `PLANNED_CHECKS.md` to find your check
2. Determine which profile it belongs to (by data source)
3. Implement check module in `src/checks/`
4. Add check to profile configuration in `config.yaml`
5. Update orchestrator mapping in `src/orchestrator.py`
6. Write unit tests in `tests/unit/`
7. Update `TASK_MATRIX.md` status (🔄 → ✅)

**Adding a New Profile:**
1. Define in `src/profiles/profile_schema.py`:
   - Add to `ProfileType` enum
   - Add dependencies to `PROFILE_DEPENDENCIES`
   - Add metadata to `PROFILE_METADATA`
2. Add check configuration to `config.yaml`
3. Write tests in `tests/unit/test_profiles.py`
4. Update `TASK_PROFILES.md` documentation

---

## 📞 Support

For questions about:
- **Installation & Setup** → This README or [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Using Profiles** → [TASK_PROFILES.md](TASK_PROFILES.md) or [PROFILE_QUICK_REFERENCE.md](PROFILE_QUICK_REFERENCE.md)
- **Technical Details** → [TASK_MATRIX.md](TASK_MATRIX.md)
- **Roadmap** → [LAUNCH_PLAN.md](LAUNCH_PLAN.md)
- **Planned Features** → [PLANNED_CHECKS.md](PLANNED_CHECKS.md)

---

**Last Updated:** October 18, 2025  
**Version:** v1.1.1  
**License:** MIT

