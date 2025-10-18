# v1.1.1 Profile System - Quick Reference

## Profile Categories

### 🔵 Core Profiles (5)
Direct data retrieval from external sources
- **quick-whois** - Fast registration check (DAS protocol, ~0.02s)
- **whois** - Full registration data (DAS + WHOIS port 43, ~0.10s)
- **dns** - DNS records (A, AAAA, MX, TXT, etc.)
- **http** - HTTP response & headers
- **ssl** - SSL/TLS certificate info

### 🟢 Analysis Profiles (5)
Process & analyze core data
- **headers** - HTTP header analysis (requires: http)
- **content** - Page content analysis (requires: http)
- **infrastructure** - Server & hosting analysis (requires: dns, http)
- **technology** - Technology stack detection (requires: http, content)
- **seo** - SEO analysis (requires: http, content)

### 🟡 Intelligence Profiles (6)
Business insights & advanced analysis
- **security** - Security posture (requires: http, headers, ssl)
- **compliance** - Compliance checks (requires: http, content, headers)
- **business** - Business intelligence (requires: whois, http, content)
- **language** - Language detection (requires: http, content)
- **fingerprinting** - Fingerprinting analysis (requires: http, content)
- **clustering** - Domain clustering (requires: dns, whois)

### 🔴 Meta Profiles (6)
Pre-configured combinations

| Profile | Profiles Included | Use Case | Duration |
|---------|------------------|----------|----------|
| **quick-check** | quick-whois, http | Fast domain filtering | 0.1-0.5s |
| **standard** | whois, dns, http, ssl, seo | Standard audit | 4-12s |
| **technical-audit** | 8 tech profiles | Deep technical analysis | 10-25s |
| **business-research** | 7 business profiles | Competitor research | 8-20s |
| **complete** | All non-meta profiles | Full analysis | 20-45s |
| **monitor** | quick-whois, http | Continuous monitoring | 0.1-0.5s |

**v1.1.1 Changes:**
- `quick-check` and `monitor` now use `quick-whois` instead of `whois` (12x faster)
- `standard` still uses full `whois` for detailed data

## CLI Usage

```bash
# Single profile
python3 -m src.orchestrator --domain example.com --profiles whois

# Multiple profiles (comma-separated)
python3 -m src.orchestrator --domain example.com --profiles whois,dns,ssl

# Meta profile
python3 -m src.orchestrator --domain example.com --profiles quick-check

# Complete analysis
python3 -m src.orchestrator --domain example.com --profiles complete

# Multiple domains with profile
python3 -m src.orchestrator --file domains.txt --profiles standard
```

## Common Use Cases

### 🚀 Quick Domain Check
```bash
--profiles quick-check
```
Perfect for: New domain discovery, quick validation

### 📊 Standard Website Audit
```bash
--profiles standard
```
Perfect for: General website analysis, SEO checks

### 🔒 Security Assessment
```bash
--profiles whois,dns,http,ssl,security
```
Perfect for: Security audits, vulnerability assessment

### 💼 Business Intelligence
```bash
--profiles business-research
```
Perfect for: Competitor analysis, market research

### 🔧 Technical Deep Dive
```bash
--profiles technical-audit
```
Perfect for: Infrastructure analysis, tech stack discovery

### 🎯 Custom Analysis
```bash
--profiles whois,dns,ssl,compliance
```
Mix and match any profiles for your specific needs!

## Python API

### Get Execution Plan
```python
from profiles.profile_loader import get_profile_execution_plan

plan = get_profile_execution_plan(['technical-audit'])
print(f"Will execute {plan['total_profiles']} profiles")
print(f"Estimated duration: {plan['estimated_duration']}")
print(f"Execution order: {plan['execution_order']}")
```

### Validate Profile Combination
```python
from profiles.profile_loader import validate_profile_combination

is_valid, error = validate_profile_combination(['whois', 'dns'])
if is_valid:
    print("Valid combination!")
else:
    print(f"Invalid: {error}")
```

### Expand Meta Profiles
```python
from profiles.profile_loader import expand_meta_profiles

profiles = expand_meta_profiles(['quick-check'])
print(f"quick-check expands to: {profiles}")
# Output: ['whois', 'http']
```

### Resolve Dependencies
```python
from profiles.profile_loader import resolve_profile_dependencies

# Request headers, automatically adds http dependency
resolved = resolve_profile_dependencies(['headers'])
print(resolved)
# Output: ['http', 'headers']
```

## Database Queries

### Check Profile Usage Stats
```sql
SELECT * FROM profile_execution_stats
ORDER BY execution_count DESC;
```

### Most Common Profile Combinations
```sql
SELECT 
    profiles_combination,
    combination_count,
    avg_duration
FROM profile_combinations
ORDER BY combination_count DESC
LIMIT 10;
```

### Profile Dependency Analysis
```sql
SELECT * FROM profile_dependency_stats
WHERE dependencies_added > 0;
```

### Recent Profile Executions
```sql
SELECT 
    d.domain_name,
    r.profiles_requested,
    r.profiles_executed,
    r.checked_at
FROM results r
JOIN domains d ON r.domain_id = d.id
WHERE r.profiles_requested IS NOT NULL
ORDER BY r.checked_at DESC
LIMIT 20;
```

## Tips & Best Practices

### 🎯 Choose the Right Profile
- Use **quick-check** for bulk domain validation
- Use **standard** for regular website audits
- Use **technical-audit** when you need infrastructure details
- Use **complete** when you need everything

### ⚡ Performance Optimization
- Profiles in the same parallel group run concurrently
- Core profiles (whois, dns, http, ssl) have no dependencies
- Analysis profiles reuse core data (no duplicate API calls)
- Meta profiles are optimized for common use cases

### 🔧 Custom Combinations
You can mix and match any profiles:
```bash
# Just SSL and security
--profiles ssl,security

# Business focus
--profiles whois,http,business,language

# Tech stack only
--profiles http,content,technology
```

### 📊 Monitor Usage
Use the analytics views to:
- Identify most-used profiles
- Find slow profile combinations
- Optimize your meta profiles
- Track dependency resolution patterns

## Troubleshooting

### Unknown profile error
```
Error: Unknown profile: invalid
```
**Solution**: Use one of the 21 valid profile names (see categories above)

### Validation fails
```bash
python3 test_v10_simple.py
```
All tests should pass (15/15)

### Database migration needed
```bash
cd db
./migrate_v10.sh
```
Choose option 2 for clean migration

### Check database state
```bash
psql $DATABASE_URL -c "SELECT * FROM validate_profile_data();"
```
All checks should return PASS

## Profile Dependencies Reference

```
Core (no dependencies):
  - quick-whois, whois, dns, http, ssl

Analysis:
  - headers → http
  - content → http
  - infrastructure → dns, http
  - technology → http, content
  - seo → http, content

Intelligence:
  - security → http, headers, ssl
  - compliance → http, content, headers
  - business → whois, http, content
  - language → http, content
  - fingerprinting → http, content
  - clustering → dns, whois

Meta (see table above for constituent profiles)
```

## WHOIS Protocol Choice (v1.1.1)

**quick-whois** vs **whois** - When to use which?

| Feature | quick-whois | whois |
|---------|-------------|-------|
| **Protocol** | DAS only | DAS + WHOIS port 43 |
| **Speed** | ~0.02s | ~0.10s |
| **Rate Limit** | 4/sec (relaxed) | 100/30min (strict) |
| **Data Returned** | Registration status only | Full data (registrar, contacts, dates, nameservers) |
| **Best For** | Bulk filtering, monitoring | Detailed analysis, research |

**Recommendations:**
- Use `quick-whois` for: Initial domain filtering, change monitoring, bulk scans
- Use `whois` for: Detailed ownership research, contact info, compliance checks
- Meta profiles: `quick-check` and `monitor` use quick-whois; `standard` uses full whois

## More Information

- **Full Profile Guide**: [TASK_PROFILES.md](TASK_PROFILES.md)
- **Check Mappings**: [TASK_MATRIX.md](TASK_MATRIX.md)
- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Roadmap**: [LAUNCH_PLAN.md](LAUNCH_PLAN.md)

---

**Last Updated:** October 18, 2025  
**Version:** v1.1.1

---

**v0.10 Composable Profile System** | Ready for production use ✅
