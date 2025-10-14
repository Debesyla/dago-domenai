# v0.8 Optimization Design Document

## Overview
Version 0.8 introduces intelligent check orchestration that skips expensive checks for domains that are unregistered or inactive. This significantly improves performance when analyzing large domain lists.

## Problem Statement
Currently, the system runs all checks (status, redirects, robots, sitemap, SSL) on every domain, regardless of whether the domain is:
- Registered (owns a domain name)
- Active (actually hosting a website)

This wastes resources checking sitemaps, SSL certificates, and robots.txt for:
- Unregistered domains (not even owned)
- Inactive domains (redirecting elsewhere or not functioning)
- Parked domains (placeholder pages)

## Solution Architecture

### 1. Database Schema Changes

Add two new columns to the `domains` table:

```sql
ALTER TABLE domains 
ADD COLUMN is_registered BOOLEAN DEFAULT NULL,
ADD COLUMN is_active BOOLEAN DEFAULT NULL;
```

**Field Meanings:**
- `is_registered = NULL` → Not yet checked
- `is_registered = TRUE` → Domain is registered (WHOIS shows ownership)
- `is_registered = FALSE` → Domain is not registered/available
- `is_active = NULL` → Not yet checked (or not applicable if unregistered)
- `is_active = TRUE` → Domain has active website
- `is_active = FALSE` → Domain redirects away or doesn't respond properly

### 2. Check Execution Flow

```
START
  ↓
WHOIS Check (v0.8 placeholder, v0.8.1 real)
  ↓
is_registered?
  ├─ NO → Save result, STOP ⛔
  ↓
 YES
  ↓
Active Check (v0.8 placeholder, v0.8.2 real)
  ↓
is_active?
  ├─ NO → Save result, STOP ⛔
  ↓
 YES
  ↓
Run Full Check Suite:
  - Status Check
  - Redirect Check
  - Robots Check
  - Sitemap Check
  - SSL Check
  ↓
Save result, STOP ✅
```

### 3. Check Implementations

#### v0.8: Placeholder Checks

**whois_check.py (Placeholder)**
```python
# Always returns registered=True for now
# Real implementation in v0.8.1
return {
    'registered': True,
    'placeholder': True,
    'message': 'Real WHOIS check in v0.8.1'
}
```

**active_check.py (Placeholder)**
```python
# Returns active based on simple status check
# Real implementation in v0.8.2
status_result = await run_status_check(domain, config)
return {
    'active': status_result.get('ok', False),
    'placeholder': True,
    'message': 'Real activity detection in v0.8.2'
}
```

#### v0.8.1: Real WHOIS Check

```python
return {
    'registered': True/False,
    'registrar': 'GoDaddy', 
    'expires_at': '2026-01-15',
    'days_until_expiry': 123,
    'nameservers': ['ns1.example.com', ...],
    'error': 'Optional error message'
}
```

#### v0.8.2: Real Activity Check

```python
# Analyzes status + redirect to determine activity
return {
    'active': True/False,
    'reason': 'redirects_to_different_domain' | 'responds_normally' | 'connection_error',
    'final_domain': 'augalyn.lt',  # If redirected
    'same_domain': False,  # True if www.example.com → example.com
    'error': 'Optional error message'
}
```

**Activity Detection Logic:**
- **ACTIVE** if:
  - HTTP 200-299 status
  - No redirect, OR redirects within same domain (www, https upgrade)
- **INACTIVE** if:
  - Redirects to different domain (gyvigali.lt → augalyn.lt)
  - HTTP 404, 403, 5xx errors
  - Connection timeout or SSL errors
  - Parked domain detection (TODO: v0.9?)

### 4. Orchestrator Changes

**Current Flow:**
```python
for domain in domains:
    result = new_domain_result(domain, task)
    
    # Run ALL checks
    run status_check
    run redirect_check
    run robots_check
    run sitemap_check
    run ssl_check
    
    save_result()
```

**New Flow (v0.8):**
```python
for domain in domains:
    result = new_domain_result(domain, task)
    
    # PHASE 1: Registration check
    whois_result = run_whois_check(domain, config)
    add_check_result(result, 'whois', whois_result)
    
    is_registered = whois_result.get('registered', False)
    
    if not is_registered:
        # Domain not registered - skip everything else
        update_domain_flags(domain_id, is_registered=False, is_active=False)
        save_result()
        continue
    
    # PHASE 2: Activity check
    active_result = run_active_check(domain, config)
    add_check_result(result, 'active', active_result)
    
    is_active = active_result.get('active', False)
    
    if not is_active:
        # Domain inactive - skip remaining checks
        update_domain_flags(domain_id, is_registered=True, is_active=False)
        save_result()
        continue
    
    # PHASE 3: Full check suite (only for active domains)
    update_domain_flags(domain_id, is_registered=True, is_active=True)
    
    run status_check
    run redirect_check
    run robots_check
    run sitemap_check
    run ssl_check
    
    save_result()
```

### 5. Database Function Updates

**New function:**
```python
def update_domain_flags(
    db_url: str,
    domain: str,
    is_registered: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> bool:
    """Update domain registration and activity flags"""
    # UPDATE domains SET is_registered = ?, is_active = ? WHERE domain_name = ?
```

**Modified function:**
```python
def get_or_create_domain(cursor, domain: str) -> int:
    """Now includes is_registered and is_active fields (defaults to NULL)"""
```

### 6. Configuration Changes

Add to `config.yaml`:
```yaml
checks:
  whois:
    enabled: true
    timeout: 10
  active:
    enabled: true
  # ... existing checks
```

## Performance Impact

**Example: 100 domain list**
- 20 unregistered domains → Skip 5 checks each = **100 checks saved**
- 30 inactive domains → Skip 4 checks each = **120 checks saved**
- 50 active domains → Run all 7 checks = **350 checks run**

**Total: 470 checks vs 700 checks = 33% reduction** 🚀

With real-world domain lists containing many expired/parked domains, savings could be 50%+.

## Migration Path

### v0.8 (Placeholders)
- Add database columns
- Implement placeholder checks
- Add orchestrator logic
- Test bailout flow

### v0.8.1 (Real WHOIS)
- Add `python-whois` dependency
- Implement real WHOIS queries
- Handle rate limiting
- Parse expiration dates

### v0.8.2 (Real Activity Detection)
- Implement domain comparison logic
- Detect parked domains
- Smart redirect analysis
- Better error categorization

## Testing Strategy

### Test Domains Needed:
1. **Registered + Active**: `example.com`, `google.com`
2. **Registered + Inactive (redirect)**: `gyvigali.lt` → `augalyn.lt`
3. **Registered + Inactive (error)**: `test.lt` (SSL issues)
4. **Unregistered**: Need to find truly unregistered domain
5. **Parked**: Need to find parked domain

### Validation:
- ✅ Unregistered domains only run whois check
- ✅ Inactive domains only run whois + active checks
- ✅ Active domains run full suite
- ✅ Database flags updated correctly
- ✅ Performance improvement measured

## Future Enhancements (Post v0.8.2)

- **v0.9**: Parked domain detection (common patterns)
- **v1.1**: Parallel check execution for active domains
- **v1.2**: Smart caching (don't re-check registration status frequently)
- **v1.3**: Bulk WHOIS queries for performance

## Summary

v0.8 introduces intelligent check orchestration:
- **Two-phase gating**: Registration → Activity → Full checks
- **Resource optimization**: Skip expensive checks for inactive domains
- **Database tracking**: Store registration and activity status
- **Incremental implementation**: Placeholders first, real checks in point releases

This sets the foundation for smarter, faster domain analysis at scale.
