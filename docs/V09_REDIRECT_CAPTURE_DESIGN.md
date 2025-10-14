# v0.9 Smart Redirect Capture - Design Document

## 🎯 Overview
Automatically discover and add new Lithuanian domains when they appear as redirect targets. This creates organic database growth through network discovery.

## 💡 Core Concept

When analyzing domain A, if it redirects to domain B:
1. Check if domain B is a `.lt` domain
2. Extract the main domain (handle subdomains intelligently)
3. If domain B doesn't exist in database → add it for future scanning
4. Track discovery source for analytics

## 📊 Example Scenarios

### Scenario 1: Basic Redirect Discovery
```
Analyzing: gyvigali.lt
Redirects to: augalyn.lt
Action: Add augalyn.lt to database
Result: Database grows by 1 domain
```

### Scenario 2: Subdomain Handling (Normal TLD)
```
Analyzing: something.lt
Redirects to: ideas.dago.lt
Action: Extract main domain → add dago.lt (not ideas.dago.lt)
Result: Avoids subdomain pollution
```

### Scenario 3: Government Domain (Special Case)
```
Analyzing: old-stat.gov.lt
Redirects to: strata.gov.lt
Action: Keep full subdomain → add strata.gov.lt
Reason: stat.gov.lt ≠ strata.gov.lt (different agencies)
Result: Preserves important government site distinction
```

### Scenario 4: Non-LT Redirect (Ignored)
```
Analyzing: oldsite.lt
Redirects to: newsite.com
Action: No capture (not .lt TLD)
Result: Focus remains on Lithuanian domains
```

### Scenario 5: Already Exists
```
Analyzing: test.lt
Redirects to: example.com
Action: Check database → example.com already exists
Result: No duplicate, but record discovery relationship
```

## 🛠️ Technical Implementation

### 1. Domain Extraction Utility (`utils/domain_utils.py`)

```python
from urllib.parse import urlparse
from typing import Optional, List

KEEP_SUBDOMAIN_PATTERNS = ['.gov.lt', '.lrv.lt']
TARGET_TLDS = ['.lt']
IGNORE_DOMAINS = ['google.lt', 'facebook.com', 'youtube.com']

def extract_main_domain(url: str, keep_patterns: List[str] = None) -> str:
    """
    Extract main domain from URL with intelligent subdomain handling.
    
    Examples:
        ideas.dago.lt → dago.lt
        strata.gov.lt → strata.gov.lt (kept)
        www.example.lt → example.lt
    """
    if keep_patterns is None:
        keep_patterns = KEEP_SUBDOMAIN_PATTERNS
    
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.path
    
    # Check if we should keep subdomain
    for pattern in keep_patterns:
        if hostname.endswith(pattern):
            return hostname  # Keep full domain
    
    # Strip subdomain - keep only domain.tld
    parts = hostname.split('.')
    if len(parts) > 2:
        # Keep last two parts (domain.tld)
        return '.'.join(parts[-2:])
    
    return hostname


def is_lithuanian_domain(domain: str) -> bool:
    """Check if domain is Lithuanian (.lt)"""
    return domain.endswith('.lt')


def should_capture_domain(
    source_domain: str, 
    target_domain: str,
    ignore_list: List[str] = None
) -> bool:
    """
    Determine if target domain should be captured.
    
    Rules:
    - Must be .lt domain
    - Must be different from source
    - Must not be in ignore list (common services)
    """
    if ignore_list is None:
        ignore_list = IGNORE_DOMAINS
    
    # Same domain - don't capture
    if source_domain == target_domain:
        return False
    
    # Not Lithuanian - don't capture
    if not is_lithuanian_domain(target_domain):
        return False
    
    # In ignore list - don't capture
    if target_domain in ignore_list:
        return False
    
    return True
```

### 2. Database Functions (`utils/db.py`)

```python
def add_discovered_domain(
    db_url: str,
    domain: str,
    discovered_from: str,
    discovery_method: str = 'redirect'
) -> bool:
    """
    Add a newly discovered domain to the database.
    
    Args:
        db_url: Database connection string
        domain: New domain to add
        discovered_from: Source domain that led to discovery
        discovery_method: How it was discovered (redirect, link, etc.)
    
    Returns:
        True if added, False if already exists or error
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            # Check if domain already exists
            cursor.execute(
                "SELECT id FROM domains WHERE domain_name = %s",
                (domain,)
            )
            
            if cursor.fetchone():
                logger.debug(f"Domain {domain} already exists")
                return False
            
            # Add new domain
            cursor.execute(
                """
                INSERT INTO domains (domain_name, created_at, updated_at)
                VALUES (%s, NOW(), NOW())
                """,
                (domain,)
            )
            
            logger.info(f"✨ Discovered new domain: {domain} (from {discovered_from})")
            
            # TODO: Track discovery in separate table for analytics
            # INSERT INTO domain_discoveries (domain, source, method, discovered_at)
            
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Failed to add discovered domain {domain}: {e}")
        return False


def get_discovery_stats(db_url: str) -> Dict[str, Any]:
    """
    Get statistics about domain discovery.
    
    Returns:
        Dict with discovery metrics
    """
    # TODO: Implement when domain_discoveries table exists
    # - Total discovered domains
    # - Top sources (which domains led to most discoveries)
    # - Discovery rate over time
    pass
```

### 3. Orchestrator Integration

```python
async def process_domain(domain: str, config: dict, logger) -> dict:
    """Process domain with redirect capture"""
    
    # ... existing check logic ...
    
    # After redirect check completes
    if 'redirects' in result['checks']:
        redirect_data = result['checks']['redirects']
        final_url = redirect_data.get('final_url')
        
        if final_url and not redirect_data.get('error'):
            # Extract target domain
            target_domain = extract_main_domain(
                final_url,
                config.get('redirect_capture', {}).get('keep_subdomains_for', [])
            )
            
            # Check if we should capture it
            if should_capture_domain(domain, target_domain):
                # Add to database
                db_config = get_database_config(config)
                db_url = db_config.get('postgres_url')
                
                if add_discovered_domain(db_url, target_domain, domain, 'redirect'):
                    logger.info(f"📍 Discovered: {target_domain} from {domain}")
    
    # ... continue with remaining checks ...
```

### 4. Configuration (`config.yaml`)

```yaml
redirect_capture:
  enabled: true
  
  # Only capture these TLDs
  target_tlds:
    - '.lt'
  
  # Keep subdomains for these patterns
  keep_subdomains_for:
    - '.gov.lt'
    - '.lrv.lt'
    # Add more as needed: '.edu.lt', '.mil.lt', etc.
  
  # Don't capture these common services
  ignore_common_services:
    - 'google.lt'
    - 'facebook.com'
    - 'youtube.com'
    - 'linkedin.com'
    - 'twitter.com'
```

## 📊 Database Schema Enhancement (Optional)

Add tracking table for analytics:

```sql
CREATE TABLE IF NOT EXISTS domain_discoveries (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id),
    discovered_from VARCHAR(255),  -- Source domain
    discovery_method VARCHAR(50),  -- 'redirect', 'link', 'user_submission'
    discovered_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_discoveries_domain ON domain_discoveries(domain_id);
CREATE INDEX idx_discoveries_source ON domain_discoveries(discovered_from);
```

## 🎯 Expected Impact

### Database Growth
With 1000 Lithuanian domains analyzed:
- ~10-15% redirect to other .lt domains
- Discover 100-150 new domains automatically
- Creates network effect: more domains → more discoveries

### Analytics Insights
- **Top Hub Domains**: Which domains redirect to most others
- **Discovery Chains**: Map redirect networks
- **Growth Rate**: Organic database expansion over time

## 🧪 Testing Strategy

### Test Cases

**Test 1: Basic Redirect Capture**
```
Domain: gyvigali.lt
Expected: Discovers and adds augalyn.lt
```

**Test 2: Subdomain Stripping**
```
Domain: test.lt
Redirects to: blog.example.lt
Expected: Adds example.lt (not blog.example.lt)
```

**Test 3: Government Domain Preservation**
```
Domain: old.gov.lt
Redirects to: stat.gov.lt
Expected: Adds stat.gov.lt (keeps subdomain)
```

**Test 4: Duplicate Prevention**
```
Domain: test1.lt
Redirects to: existing-domain.lt
Expected: No addition (already exists)
```

**Test 5: Non-LT Filtering**
```
Domain: oldsite.lt
Redirects to: newsite.com
Expected: No capture (not .lt)
```

**Test 6: Same Domain (www)**
```
Domain: example.lt
Redirects to: www.example.lt
Expected: No capture (same domain)
```

## 🔮 Future Enhancements

### v0.9.1: Link Discovery
- Parse HTML for outbound links
- Discover domains linked from content
- Build domain relationship graph

### v0.9.2: Discovery Analytics
- Dashboard showing discovery networks
- Visualize redirect chains
- Identify hub domains (many outbound redirects)

### v3.0: User Submissions Integration
- User submits domain via web form
- Uses same `extract_main_domain()` logic
- Queue for analysis
- Show cached results if exists

## ✅ Success Criteria

v0.9 is successful when:
- [ ] `domain_utils.py` correctly extracts main domains
- [ ] Government subdomains (.gov.lt) preserved
- [ ] Non-.lt redirects ignored
- [ ] Discovered domains added to database
- [ ] No duplicate domains created
- [ ] Discovery logged for tracking
- [ ] Config allows customization
- [ ] Tests pass for all scenarios

## 📝 Implementation Checklist

- [ ] Create `src/utils/domain_utils.py`
- [ ] Add `extract_main_domain()` function
- [ ] Add `is_lithuanian_domain()` function
- [ ] Add `should_capture_domain()` function
- [ ] Update `src/utils/db.py` with `add_discovered_domain()`
- [ ] Update `src/orchestrator.py` to call capture logic
- [ ] Add `redirect_capture` section to `config.yaml`
- [ ] Write tests for domain extraction
- [ ] Test with gyvigali.lt → augalyn.lt
- [ ] Verify database growth
- [ ] Update documentation

---

**This feature creates a self-expanding domain database through intelligent network discovery!** 🌐✨
