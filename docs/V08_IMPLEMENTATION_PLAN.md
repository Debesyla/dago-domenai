# v0.8 Implementation Plan Summary

## 🎯 Goal
Optimize check process with early bailout logic - don't waste resources on unregistered or inactive domains.

## 📋 Implementation Checklist

### 1. Database Migration ✅
- [x] Created migration script: `db/migrations/v0.8_add_domain_flags.sql`
- [ ] Run migration: `psql $DATABASE_URL -f db/migrations/v0.8_add_domain_flags.sql`
- [ ] Verify columns added: `is_registered`, `is_active`

### 2. Placeholder Checks
- [ ] Create `src/checks/whois_check.py` (placeholder)
  - Returns `{registered: True, placeholder: True}`
  - Will be replaced in v0.8.1
  
- [ ] Create `src/checks/active_check.py` (placeholder)
  - Uses status check to determine activity
  - Returns `{active: bool, placeholder: True}`
  - Will be replaced in v0.8.2

### 3. Database Functions
- [ ] Add `update_domain_flags()` to `src/utils/db.py`
  - Update `is_registered` and `is_active` for a domain
  
- [ ] Modify `get_or_create_domain()` if needed
  - Ensure new columns are handled

### 4. Orchestrator Logic
- [ ] Update `src/orchestrator.py`:
  - Import new checks
  - Add Phase 1: WHOIS check
  - Add early bailout if not registered
  - Add Phase 2: Active check  
  - Add early bailout if not active
  - Phase 3: Full checks only for active domains
  - Call `update_domain_flags()` after each phase

### 5. Configuration
- [ ] Update `config.yaml`:
  - Add `checks.whois.enabled`
  - Add `checks.active.enabled`

### 6. Testing
- [ ] Test with registered+active domain (example.com)
- [ ] Test with registered+inactive domain (test.lt)
- [ ] Test with redirect domain (gyvigali.lt)
- [ ] Verify database flags updated correctly
- [ ] Measure performance improvement

### 7. Documentation
- [ ] Update README.md with v0.8 features
- [ ] Update version to 0.8.0 in `src/__init__.py`
- [ ] Document check flow in comments

## 🔄 Check Execution Flow

```
┌─────────────────┐
│  Start Analysis │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WHOIS Check    │
│  (Phase 1)      │
└────────┬────────┘
         │
         ▼
   Is Registered?
         │
    ┌────┴────┐
    │ NO      │ YES
    ▼         ▼
  STOP    ┌─────────────────┐
          │  Active Check   │
          │  (Phase 2)      │
          └────────┬────────┘
                   │
                   ▼
             Is Active?
                   │
              ┌────┴────┐
              │ NO      │ YES
              ▼         ▼
            STOP    ┌─────────────────┐
                    │  Full Checks    │
                    │  (Phase 3)      │
                    │  - Status       │
                    │  - Redirect     │
                    │  - Robots       │
                    │  - Sitemap      │
                    │  - SSL          │
                    └─────────────────┘
```

## 📊 Expected Results

### Before v0.8:
- Every domain runs 5 checks
- 100 domains = 500 check operations

### After v0.8:
- Unregistered: 1 check (whois only)
- Inactive: 2 checks (whois + active)
- Active: 7 checks (whois + active + 5 full checks)

**Example with 100 domains:**
- 20 unregistered → 20 checks
- 30 inactive → 60 checks  
- 50 active → 350 checks
- **Total: 430 vs 500 = 14% reduction**

With real-world lists (more inactive domains), savings could be 30-50%+!

## 🚀 Future Versions

### v0.8.1 - Real WHOIS Check
- Add `python-whois` dependency
- Query actual WHOIS servers
- Parse registration details
- Extract expiration dates

### v0.8.2 - Smart Activity Detection
- Analyze redirect destination
- Detect parked domains
- Compare source vs final domain
- Better inactive detection

## 📝 Testing Commands

```bash
# Run migration
psql $DATABASE_URL -f db/migrations/v0.8_add_domain_flags.sql

# Test single domain
python -m src.orchestrator --domain example.com

# Test full list
python -m src.orchestrator domains.txt

# Check database flags
python -c "
from src.utils.db import get_domains
from src.utils.config import load_config, get_database_config
import os

config = load_config()
db_url = os.environ.get('DATABASE_URL', get_database_config(config)['postgres_url'])
domains = get_domains(db_url)

for d in domains:
    print(f\"{d['domain_name']}: registered={d.get('is_registered')}, active={d.get('is_active')}\")
"

# Query specific domain
python query_db.py domain example.com
```

## ✅ Definition of Done

v0.8 is complete when:
- [ ] Migration script run successfully
- [ ] Placeholder checks implemented
- [ ] Orchestrator has 3-phase logic
- [ ] Database flags updated correctly
- [ ] All tests pass
- [ ] Performance improvement measurable
- [ ] Documentation updated
- [ ] Tagged and committed

---

**Ready to implement v0.8!** 🚀
