# Rate Limiting Behavior in DAGO v1.1

## Quick Answer

**When WHOIS rate limit is hit:**
- ❌ **Does NOT stop** the entire process
- ❌ **Does NOT wait** for rate limit to clear
- ✅ **Skips gracefully** - returns partial data and continues with other checks

---

## Detailed Explanation

### Current Behavior (v1.1)

When you run:
```bash
python3 -m src.orchestrator domains.txt --profiles whois,dns,ssl
```

Here's what happens for each domain:

```
Domain 1:
  1. WHOIS check (DAS + WHOIS) → ✅ Success (0.10s)
  2. DNS check → ✅ Runs normally
  3. SSL check → ✅ Runs normally
  
Domain 2:
  1. WHOIS check (DAS + WHOIS) → ✅ Success (0.10s)
  2. DNS check → ✅ Runs normally
  3. SSL check → ✅ Runs normally
  
... (repeat 100 times)

Domain 101:
  1. WHOIS check:
     - DAS (fast) → ✅ "registered" (0.02s)
     - WHOIS (detailed) → ❌ Rate limited!
     - Returns: DAS data only (minimal info)
     - Sets flag: whois_rate_limited = true
  2. DNS check → ✅ Runs normally (not affected)
  3. SSL check → ✅ Runs normally (not affected)
  
Domain 102-10000:
  - Same as Domain 101
  - WHOIS returns minimal data
  - Other checks continue normally
```

---

## Rate Limit Implementation

### Token Bucket Algorithm

```python
class TokenBucket:
    # Starts with 100 tokens
    # Refills at rate: 100 tokens / 1800 seconds = 0.055 tokens/sec
    # = 1 token every ~18 seconds
    
    async def acquire(self) -> bool:
        # Try to get a token
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True  # ✅ Query allowed
        
        return False  # ❌ Rate limited
```

### What Happens When Rate Limited

```python
# In WHOISClient.query():

if not await self.rate_limiter.acquire():
    # Rate limit hit!
    time_until = self.rate_limiter.time_until_token()
    
    return {
        'error': 'rate_limit_exceeded',
        'message': f'Rate limit exceeded. Try again in {time_until:.0f} seconds',
        'time_until_available': time_until
    }

# In run_whois_check():

whois_data = await whois_client.query(domain)

if 'error' in whois_data:
    # Rate limited - return minimal data
    logger.warning(f"WHOIS rate limited for {domain}")
    
    return {
        'status': 'registered',
        'registration': {'status': 'registered'},  # Minimal from DAS
        'meta': {
            'whois_rate_limited': True,  # ⚠️ Flag set
            'whois_error': 'rate_limit_exceeded'
        }
    }
    # ✅ Process continues with next check!
```

---

## Example Scenario: 10,000 Domains

### Setup
```bash
python3 -m src.orchestrator domains.txt --profiles whois,dns,ssl
```

### Timeline

**Minutes 0-30: First 100 domains**
```
✅ Domain 1-100: Full WHOIS data (DAS + port 43)
   - WHOIS token count: 100 → 0
   - All data captured
```

**Minutes 30-60: Domains 101-200**
```
⚠️  Domain 101-200: Partial WHOIS data (DAS only)
   - WHOIS queries denied (no tokens)
   - Returns: DAS status only
   - Flag: whois_rate_limited = true
   - DNS and SSL checks: ✅ Still run normally!
   - WHOIS tokens slowly refilling: 0 → ~6 tokens
```

**Minutes 60-90: Domains 201-300**
```
✅ Domain 201-206: Full WHOIS data (6 tokens refilled)
⚠️  Domain 207-300: Partial WHOIS data
   - DNS and SSL: ✅ Still working
   - WHOIS tokens: 6 → 12 tokens
```

**Pattern continues...**

---

## Key Points

### 1. **No Blocking or Waiting**
```python
# The orchestrator processes domains sequentially:
for domain in domains:
    result = await process_domain(domain, config, logger, profiles)
    # ⬆️ If WHOIS is rate limited, this still completes quickly
    # It just returns partial data instead of waiting
```

### 2. **Graceful Degradation**
```json
// Rate limited result (still valid!)
{
  "status": "registered",
  "registration": {
    "status": "registered"  // Minimal info from DAS
  },
  "meta": {
    "whois_rate_limited": true,  // ⚠️ You can query later!
    "whois_error": "rate_limit_exceeded"
  }
}
```

### 3. **Other Checks Unaffected**
- DNS queries: ✅ Continue normally
- SSL checks: ✅ Continue normally
- HTTP checks: ✅ Continue normally
- Only WHOIS is affected

### 4. **Token Refill Happens Automatically**
- Every ~18 seconds: +1 token
- After 30 minutes: Full 100 tokens restored
- No manual intervention needed

---

## Practical Strategy for 10,000 Domains

### Option A: Continuous Scanning (Recommended)
```bash
# Just start the scan and let it run
python3 -m src.orchestrator domains.txt --profiles whois,dns,ssl

# What happens:
# - First 100 domains: Full WHOIS data
# - Next 9,900 domains: Partial WHOIS (DAS only) + Full DNS + Full SSL
# - WHOIS data accumulates as tokens refill
# - Total time: ~10-15 hours (not blocked by rate limit!)
```

### Option B: Re-scan for Missing WHOIS Data
```bash
# After initial scan, find domains with incomplete WHOIS:
psql $DATABASE_URL -c "
  SELECT d.domain_name 
  FROM domains d
  JOIN results r ON d.id = r.domain_id
  WHERE r.data->'whois'->'meta'->>'whois_rate_limited' = 'true'
" > missing_whois.txt

# Re-scan later (with fresh rate limit):
python3 -m src.orchestrator missing_whois.txt --profiles whois
```

### Option C: Slower Scan to Stay Under Limit
```python
# Add delay between domains (future feature)
# Scan 100 domains per 30 minutes = 1 domain every 18 seconds
# This would ensure full WHOIS data for all domains
# But take 50 hours for 10,000 domains
```

---

## Database Flags

You can identify rate-limited results:

```sql
-- Find domains with incomplete WHOIS data
SELECT 
    d.domain_name,
    r.data->'whois'->'meta'->>'whois_rate_limited' as was_rate_limited,
    r.checked_at
FROM results r
JOIN domains d ON r.domain_id = d.id
WHERE r.data->'whois'->'meta'->>'whois_rate_limited' = 'true'
ORDER BY r.checked_at DESC;
```

---

## Summary

### Current Behavior (v1.1):
✅ **Non-blocking** - Process continues immediately  
✅ **Graceful** - Returns partial data instead of error  
✅ **Isolated** - Other checks (DNS, SSL) unaffected  
✅ **Transparent** - Sets `whois_rate_limited` flag  
✅ **Self-healing** - Tokens refill automatically  

### What Does NOT Happen:
❌ Process does not pause/wait  
❌ Process does not stop  
❌ Other checks are not affected  
❌ No errors thrown (graceful degradation)  

---

## Future Enhancement Ideas

If you want different behavior, we could add:

1. **Wait Mode** (not recommended)
   ```python
   # Wait for token instead of skipping
   while not await rate_limiter.acquire():
       await asyncio.sleep(18)  # Wait for next token
   ```

2. **Queue Mode**
   ```python
   # Queue rate-limited domains for later retry
   rate_limited_queue.append(domain)
   # Process queue after main scan
   ```

3. **Batch Mode**
   ```python
   # Process in batches of 100 every 30 minutes
   for batch in chunks(domains, 100):
       process_batch(batch)
       await asyncio.sleep(1800)  # Wait 30 min
   ```

**But current behavior is optimal for bulk scanning!** ✅
