# ⚠️ SUPERSEDED - v0.10 Task Profiles (Original Design)

> **⚠️ THIS DESIGN WAS SUPERSEDED**  
> This document represents the original v0.10 design using rigid task tiers (`--task basic-scan`).  
> It has been replaced by a composable profile system (`--profiles dns,ssl`).
>
> **Current Design:** See `V10_SUMMARY.md` for the implemented composable system.  
> **Technical Spec:** See `TASK_MATRIX.md` for profile definitions.  
> **User Guide:** See `TASK_PROFILES.md` for usage examples.
>
> This file is kept for historical reference only.

---

# v0.10 Task Profiles & Clean Database Schema - Original Design Document

## 🎯 Overview
Restructure the `tasks` table to use meaningful scan profiles instead of placeholder names. This creates a professional, flexible system that can grow as new checks are added.

**NOTE:** This approach was later redesigned to use composable, data-source-based profiles for better performance and flexibility.

## 📋 Current State Analysis

### What We Have Now
```sql
-- Current tasks table (messy)
tasks:
  - check_status (what does this even mean?)
  - basic-scan (but which checks?)
```

**Problems:**
- Inconsistent naming
- No clear definition of what checks run
- Can't choose scan depth
- Descriptions don't match reality
- As we add checks (v0.4, v0.5, v0.6+), tasks don't reflect them

### What We Want
```sql
-- Clean task profiles
tasks:
  - quick-check    → Fast filtering (2 checks)
  - basic-scan     → Standard analysis (5 checks)
  - full-scan      → Comprehensive (7+ checks)
  - monitor        → Lightweight tracking (2 checks)
```

**Benefits:**
- Clear purpose for each profile
- Users can choose appropriate scan depth
- Easy to add new checks to profiles
- Professional and maintainable

## 🏗️ Architecture Design

### Concept: Tasks as Scan Profiles

**Task = A predefined set of checks with a specific purpose**

```
┌─────────────────────────────────────────────────────────┐
│                    TASK PROFILES                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  quick-check:  [whois, active]                          │
│  Purpose: Fast filtering for bulk lists                 │
│  Use Case: "Is this domain even worth checking?"        │
│                                                          │
│  basic-scan:   [whois, active, status, redirects, ssl]  │
│  Purpose: Standard domain analysis                      │
│  Use Case: "Tell me about this domain"                  │
│                                                          │
│  full-scan:    [all available checks]                   │
│  Purpose: Comprehensive analysis                        │
│  Use Case: "I need to know everything"                  │
│                                                          │
│  monitor:      [status, ssl]                            │
│  Purpose: Lightweight recurring checks                  │
│  Use Case: "Alert me if something changes"              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User runs: python -m src.orchestrator domains.txt --task quick-check
  ↓
Orchestrator loads task config: quick-check = [whois, active]
  ↓
For each domain:
  ├─ Run whois check
  ├─ If not registered → STOP (early bailout from v0.8)
  ├─ Run active check
  ├─ If not active → STOP (early bailout from v0.8)
  └─ Save result with metadata: checks_performed = [whois, active]
```

## 📊 Check Matrix (TO BE DEFINED BY YOU)

This is a **placeholder** - you'll fill this in during implementation:

| Check       | quick-check | basic-scan | full-scan | monitor | Notes |
|-------------|-------------|------------|-----------|---------|-------|
| whois       | ✅          | ✅         | ✅        | ❌      | Registration check |
| active      | ✅          | ✅         | ✅        | ❌      | Activity check |
| status      | ❌          | ✅         | ✅        | ✅      | HTTP status code |
| redirects   | ❌          | ✅         | ✅        | ❌      | Redirect chain |
| ssl         | ❌          | ✅         | ✅        | ✅      | Certificate check |
| robots      | ❌          | ❌         | ✅        | ❌      | robots.txt |
| sitemap     | ❌          | ❌         | ✅        | ❌      | sitemap.xml |
| **Future:** |             |            |           |         | |
| dns         | ❌          | ❌         | ✅        | ❌      | v1.1+ |
| headers     | ❌          | ❌         | ✅        | ❌      | v1.1+ |
| content     | ❌          | ❌         | ✅        | ❌      | v1.2+ |
| screenshot  | ❌          | ❌         | ✅        | ❌      | v2.0+ |
| tech        | ❌          | ❌         | ✅        | ❌      | v1.1+ |

**Note:** This is YOUR decision to make during implementation! Balance performance vs completeness.

## 🗄️ Database Changes

### Migration Script

```sql
-- File: db/migrations/v0.10_task_profiles.sql

BEGIN;

-- Optional: Backup existing data
CREATE TABLE IF NOT EXISTS tasks_backup_v09 AS SELECT * FROM tasks;
CREATE TABLE IF NOT EXISTS results_backup_v09 AS SELECT * FROM results;

-- Clean slate
DELETE FROM results;
DELETE FROM tasks;

-- Insert new task profile definitions
INSERT INTO tasks (name, description) VALUES
('quick-check', 'Fast validation: WHOIS registration and activity status checks only. Use for bulk filtering of large domain lists.'),
('basic-scan', 'Standard analysis: Essential checks including registration, activity, HTTP status, redirects, and SSL certificate. Default scan for most domains.'),
('full-scan', 'Comprehensive analysis: All available checks including registration, activity, HTTP, redirects, SSL, robots.txt, sitemap, and future checks. Use for important domains requiring detailed analysis.'),
('monitor', 'Recurring monitoring: Lightweight checks for tracking status changes and SSL certificate expiration. Use for ongoing surveillance of known domains.');

-- Reset domains for clean re-scanning
UPDATE domains 
SET updated_at = NULL, 
    is_registered = NULL, 
    is_active = NULL;

-- Add helpful comments
COMMENT ON TABLE tasks IS 'Scan profiles defining different depths of domain analysis';
COMMENT ON COLUMN tasks.name IS 'Profile name used in CLI and configuration';
COMMENT ON COLUMN tasks.description IS 'Human-readable explanation of profile purpose and use case';

COMMIT;
```

### Result Schema Enhancement

Add `checks_performed` to track which checks actually ran:

```json
{
  "domain": "example.com",
  "meta": {
    "timestamp": "2025-10-14T12:00:00Z",
    "task": "basic-scan",
    "checks_performed": ["whois", "active", "status", "redirects", "ssl"],
    "checks_skipped": ["robots", "sitemap"],
    "skip_reason": "Not included in basic-scan profile",
    "execution_time_sec": 2.5,
    "status": "success",
    "schema_version": "1.0"
  },
  "checks": {
    "whois": { "registered": true, ... },
    "active": { "active": true, ... },
    "status": { "code": 200, ... },
    "redirects": { "length": 0, ... },
    "ssl": { "valid": true, ... }
  },
  "summary": {
    "reachable": true,
    "https": true,
    "grade": "A"
  }
}
```

**Why this matters:**
- Know exactly which checks ran
- Understand why some checks were skipped
- Query: "Show me all domains scanned with full-scan"
- Analytics: "How many domains needed only quick-check?"

## ⚙️ Configuration Structure

### config.yaml

```yaml
# Default orchestrator settings
orchestrator:
  default_task: basic-scan  # Used when --task not specified
  parallel: false           # Future: parallel execution

# Task Profile Definitions
# YOU WILL CUSTOMIZE THIS DURING IMPLEMENTATION
tasks:
  quick-check:
    description: "Fast validation for bulk filtering"
    use_case: "Initial screening of large domain lists"
    checks:
      - whois
      - active
    # As you add checks, update this list
  
  basic-scan:
    description: "Standard domain analysis"
    use_case: "Default scan for most domains"
    checks:
      - whois
      - active
      - status
      - redirects
      - ssl
    # As you add checks, update this list
  
  full-scan:
    description: "Comprehensive analysis with all checks"
    use_case: "Detailed analysis for important domains"
    checks:
      - whois
      - active
      - status
      - redirects
      - robots
      - sitemap
      - ssl
      # Future checks will be added here:
      # - dns
      # - headers
      # - content
      # - screenshot
      # - tech_detection
  
  monitor:
    description: "Lightweight recurring monitoring"
    use_case: "Track status changes over time"
    checks:
      - status
      - ssl
    # Minimal for performance

# Individual check configurations (existing)
checks:
  whois:
    enabled: true
  active:
    enabled: true
  status:
    enabled: true
  # ... etc
```

## 🔧 Implementation Details

### Orchestrator Changes

```python
# src/orchestrator.py

def get_checks_for_task(task_name: str, config: dict) -> List[str]:
    """
    Get list of checks to perform for a given task profile.
    
    Args:
        task_name: Name of task profile (e.g., 'quick-check')
        config: Full configuration dict
        
    Returns:
        List of check names to execute
    """
    tasks = config.get('tasks', {})
    
    if task_name not in tasks:
        logger.warning(f"Unknown task: {task_name}, using basic-scan")
        task_name = 'basic-scan'
    
    task_config = tasks.get(task_name, {})
    checks = task_config.get('checks', [])
    
    logger.info(f"Task '{task_name}': {len(checks)} checks to perform")
    return checks


async def process_domain(domain: str, config: dict, logger, task_name: str = None) -> dict:
    """Process domain with specified task profile"""
    
    if task_name is None:
        task_name = config.get('orchestrator', {}).get('default_task', 'basic-scan')
    
    # Get checks for this task
    checks_to_run = get_checks_for_task(task_name, config)
    checks_performed = []
    checks_skipped = []
    
    # Initialize result
    result = new_domain_result(domain, task_name)
    
    # Run each check if it's in the profile
    for check_name in ['whois', 'active', 'status', 'redirects', 'robots', 'sitemap', 'ssl']:
        if check_name in checks_to_run:
            # Run the check
            check_result = await run_check(check_name, domain, config)
            add_check_result(result, check_name, check_result)
            checks_performed.append(check_name)
        else:
            checks_skipped.append(check_name)
    
    # Add metadata
    result['meta']['checks_performed'] = checks_performed
    result['meta']['checks_skipped'] = checks_skipped
    result['meta']['skip_reason'] = f"Not included in {task_name} profile"
    
    return result
```

### CLI Enhancement

```python
# Add --task argument
parser.add_argument(
    '--task',
    choices=['quick-check', 'basic-scan', 'full-scan', 'monitor'],
    default=None,
    help='Scan profile to use (default: basic-scan)'
)

# Usage examples:
# python -m src.orchestrator domains.txt
# python -m src.orchestrator domains.txt --task quick-check
# python -m src.orchestrator --domain example.com --task full-scan
```

### Query Tools Update

```python
# query_db.py enhancements

# Filter by task
python query_db.py latest --task full-scan

# Show which checks were performed
python query_db.py domain example.com --show-checks

# Output:
"""
Results for: example.com
  Task: basic-scan
  Checks performed: whois, active, status, redirects, ssl
  Checks skipped: robots, sitemap
  Status: success
"""
```

## 🧪 Testing Strategy

### Test Scenarios

**Test 1: quick-check Profile**
```bash
python -m src.orchestrator --domain test.lt --task quick-check
Expected: Only whois and active checks run
Expected: checks_performed = ["whois", "active"]
```

**Test 2: basic-scan Profile (Default)**
```bash
python -m src.orchestrator --domain example.com
Expected: whois, active, status, redirects, ssl checks run
Expected: task = "basic-scan"
```

**Test 3: full-scan Profile**
```bash
python -m src.orchestrator --domain github.com --task full-scan
Expected: All 7 checks run (whois, active, status, redirects, robots, sitemap, ssl)
Expected: checks_performed = ["whois", "active", "status", "redirects", "robots", "sitemap", "ssl"]
```

**Test 4: monitor Profile**
```bash
python -m src.orchestrator --domain example.com --task monitor
Expected: Only status and ssl checks run
Expected: Fast execution (< 1 second)
```

**Test 5: Database Consistency**
```sql
-- Verify task profiles exist
SELECT * FROM tasks;

-- Verify results reference valid tasks
SELECT DISTINCT task_id, t.name 
FROM results r 
JOIN tasks t ON r.task_id = t.id;
```

## 📈 Performance Impact

### Before v0.10:
- One task: `basic-scan`
- Always runs same checks
- No flexibility

### After v0.10:
- Four task profiles
- Choose appropriate depth
- Combined with v0.8 optimization:

**Example: 1000 domains**
```
Option 1: quick-check on all
- 2 checks × 1000 = 2,000 check operations
- Identify 500 active domains in minutes
- Then run full-scan on those 500

Option 2: basic-scan on all  
- 5 checks × 1000 = 5,000 check operations
- Get good data without deep dive

Option 3: full-scan on all
- 7+ checks × 1000 = 7,000+ check operations
- Maximum detail, longer runtime
```

**Smart workflow:**
```
1. Run quick-check on 10,000 domains → find 3,000 active
2. Run basic-scan on 3,000 active → identify 500 important
3. Run full-scan on 500 important → deep analysis
4. Run monitor on 500 important → track changes

Result: Smart resource usage, maximum insight
```

## 📚 Documentation Needs

### File: docs/TASK_PROFILES.md

```markdown
# Task Profiles Guide

## Available Profiles

### quick-check
**Purpose:** Fast validation
**Checks:** whois, active
**Use when:** Screening large lists, initial filtering
**Runtime:** ~0.5s per domain

### basic-scan
**Purpose:** Standard analysis
**Checks:** whois, active, status, redirects, ssl
**Use when:** Most common use case, balanced depth
**Runtime:** ~2-3s per domain

### full-scan
**Purpose:** Comprehensive analysis
**Checks:** All available checks
**Use when:** Important domains, detailed reporting
**Runtime:** ~5-7s per domain

### monitor
**Purpose:** Recurring monitoring
**Checks:** status, ssl
**Use when:** Tracking known domains over time
**Runtime:** ~1s per domain

## Choosing the Right Profile

| Scenario | Recommended Profile |
|----------|-------------------|
| New batch of 1000+ domains | quick-check → basic-scan |
| Single domain inquiry | basic-scan |
| Important government/business site | full-scan |
| Daily status tracking | monitor |
| After redirect discovery (v0.9) | basic-scan |

## Adding New Checks

When you implement new checks (DNS, headers, etc.):
1. Add check to appropriate profiles in config.yaml
2. Update this documentation
3. Test each profile still works
4. Consider performance impact
```

## ✅ Success Criteria

v0.10 is complete when:
- [ ] Migration script created and documented
- [ ] Four task profiles defined in database
- [ ] Check matrix documented in config.yaml
- [ ] Orchestrator loads and respects task config
- [ ] CLI accepts `--task` parameter
- [ ] Results include `checks_performed` metadata
- [ ] Query tools show task information
- [ ] Documentation explains each profile
- [ ] Tests pass for all four profiles
- [ ] Easy to add new checks to profiles

## 🔮 Future Flexibility

This design accommodates:
- **New checks** - Just add to appropriate profiles
- **New profiles** - Easy to add "government-scan", "ecommerce-scan", etc.
- **Custom profiles** - Users could define their own (future feature)
- **Profile inheritance** - full-scan could extend basic-scan (future)
- **Conditional checks** - Run check B only if check A passes (already possible with v0.8)

## 📝 Implementation Checklist

- [ ] Review check matrix, decide which checks go in which profile
- [ ] Create migration script `db/migrations/v0.10_task_profiles.sql`
- [ ] Add task definitions to `config.yaml`
- [ ] Update `src/orchestrator.py`:
  - [ ] Add `get_checks_for_task()` function
  - [ ] Modify `process_domain()` to respect task config
  - [ ] Add `checks_performed` to result metadata
- [ ] Update CLI to accept `--task` parameter
- [ ] Update `src/core/schema.py` if needed
- [ ] Update `query_db.py` to show task info
- [ ] Create `docs/TASK_PROFILES.md`
- [ ] Test all four profiles
- [ ] Run migration on database
- [ ] Update README.md

---

**This creates a professional, flexible foundation for the project!** 🎯
