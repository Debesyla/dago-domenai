# DAS vs WHOIS Protocol Analysis

**Test Date:** October 16, 2025  
**Test Domain:** debesyla.lt  
**Goal:** Determine if v1.1 goals are achievable with current DAS implementation

---

## Test Results

### DAS Protocol (port 4343) - Current Implementation
```
% .lt registry DAS service
Domain: debesyla.lt
Status: registered
```

**Data Available:**
- ✅ Domain name
- ✅ Registration status (registered/available)
- ❌ No registrar information
- ❌ No dates
- ❌ No nameservers
- ❌ No contact info

**Characteristics:**
- Ultra-fast response (66 bytes)
- Designed for bulk checking
- Rate limit: 4+ queries/second
- Perfect for: Filtering registered vs available domains

---

### Standard WHOIS (port 43) - Full Details
```
Domain:                 debesyla.lt
Status:                 registered
Registered:             2013-03-27
Expires:                2026-03-28
%
Registrar:              HOSTINGER operations, UAB
Registrar website:      https://www.hostinger.lt
Registrar email:        Techsupport@hostinger.com
%
Nameserver:             ns1.dns-parking.com
Nameserver:             ns2.dns-parking.com
```

**Data Available:**
- ✅ Domain name
- ✅ Registration status
- ✅ Registration date
- ✅ Expiration date
- ✅ Registrar name
- ✅ Registrar website
- ✅ Registrar email
- ✅ Nameservers
- ❌ No registrant organization (privacy protected)
- ❌ No updated date shown in this response

**Characteristics:**
- Full WHOIS data (887 bytes)
- **STRICT rate limit:** 100 queries per 30 minutes with IP blocking
- Perfect for: Detailed domain information

---

## V1.1 Implementation Strategy

### Current State (v1.0)
- ✅ Using DAS for fast registration status checks
- ✅ Early bailout optimization (skip unregistered domains)
- ✅ Works great for bulk filtering

### V1.1 Goals from LAUNCH_PLAN.md
Need to implement:
1. ✅ Registration status (already works via DAS)
2. ❌ Registrar name and IANA ID → **Requires WHOIS port 43**
3. ❌ Registration date → **Requires WHOIS port 43**
4. ❌ Expiration date → **Requires WHOIS port 43**
5. ❌ Updated date → **May require WHOIS port 43**
6. ❌ Registrant organization → **Requires WHOIS port 43** (if not privacy protected)
7. ❌ Registry status codes → Already have basic status
8. ❌ Privacy protection detection → **Requires WHOIS port 43**
9. ✅ Domain age calculation → Can derive from registration date

---

## Recommended Approach for V1.1

### Option A: Dual Protocol (RECOMMENDED)
**Strategy:** Use DAS for filtering, WHOIS for details

```python
async def run_whois_check(domain: str, config: dict) -> dict:
    # Step 1: Quick DAS check (existing code)
    das_result = await das_client.check_domain(domain)
    
    if not das_result['registered']:
        # Domain not registered - return early (no need for WHOIS)
        return {'status': 'available', ...}
    
    # Step 2: For registered domains, get full WHOIS data
    whois_result = await whois_client.query(domain)
    
    return {
        'status': 'registered',
        'registrar': whois_result['registrar'],
        'registration_date': whois_result['registered'],
        'expiration_date': whois_result['expires'],
        'nameservers': whois_result['nameservers'],
        'domain_age_days': calculate_age(whois_result['registered']),
        ...
    }
```

**Pros:**
- Keep fast DAS for bulk filtering
- Get detailed data only for registered domains
- Respects rate limits (only query WHOIS for ~20% of domains)
- Maintains early bailout optimization

**Cons:**
- Need to implement WHOIS port 43 client
- Must handle strict rate limiting (100 queries / 30 min)
- More complex error handling

---

### Option B: WHOIS Only
**Strategy:** Replace DAS with WHOIS for everything

**Pros:**
- Single protocol, simpler code
- Get all data in one query

**Cons:**
- **MAJOR:** Rate limit of 100 queries/30min kills bulk scanning
- Would need 75 hours to scan 150K domains (vs ~10-15 hours with DAS)
- IP blocking risk
- Loses early bailout advantage

---

## Implementation Plan for V1.1

### Recommended: Option A (Dual Protocol)

**Phase 1: Add WHOIS Port 43 Client**
1. Create `WHOISClient` class in `whois_check.py`
2. Implement rate limiting (100 queries / 30 min)
3. Parse WHOIS response for .lt domains
4. Handle errors and retries

**Phase 2: Integrate with Existing DAS Flow**
1. Keep DAS for initial registration check (fast)
2. Call WHOIS only if DAS returns `registered`
3. Add WHOIS data to result schema
4. Update database schema if needed

**Phase 3: Rate Limit Management**
1. Implement token bucket for WHOIS queries
2. Add queue system for rate-limited queries
3. Log rate limit status
4. Graceful degradation (return DAS data only if rate limited)

**Phase 4: Testing**
1. Test with small domain list (10-20 domains)
2. Verify rate limiting works
3. Test with mix of registered/unregistered
4. Measure performance impact

---

## Code Structure Preview

```python
# whois_check.py additions

class WHOISClient:
    """Standard WHOIS client for detailed domain data."""
    
    def __init__(self, server='whois.domreg.lt', port=43, timeout=10.0):
        self.server = server
        self.port = port
        self.timeout = timeout
        self.rate_limiter = TokenBucket(max_tokens=100, refill_period=1800)
    
    async def query(self, domain: str) -> Dict:
        """Query WHOIS and parse response."""
        # Check rate limit
        if not await self.rate_limiter.acquire():
            raise RateLimitError("WHOIS rate limit exceeded")
        
        # Query socket (similar to DAS)
        response = await self._query_socket(domain)
        
        # Parse WHOIS response
        return self._parse_whois(response)
    
    def _parse_whois(self, response: str) -> Dict:
        """Parse .lt WHOIS response format."""
        data = {}
        for line in response.split('\n'):
            if ':' in line and not line.startswith('%'):
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'registrar':
                    data['registrar'] = value
                elif key == 'registered':
                    data['registration_date'] = value
                elif key == 'expires':
                    data['expiration_date'] = value
                # ... etc
        
        return data
```

---

## Timeline Estimate for V1.1

- **Add WHOISClient:** 2-3 hours
- **Integration & testing:** 2-3 hours
- **Rate limit handling:** 1-2 hours
- **Documentation:** 1 hour

**Total:** ~6-9 hours of development

---

## Question for Decision

**Should we proceed with Option A (Dual Protocol) for v1.1?**

This would give us:
- Fast bulk scanning (via DAS)
- Detailed WHOIS data for registered domains
- Respects rate limits
- Achieves all v1.1 goals

Alternative: We could skip v1.1 detailed WHOIS and go straight to v1.2 (DNS) if you prefer.
