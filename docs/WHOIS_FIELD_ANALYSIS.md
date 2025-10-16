# WHOIS Field Analysis for .lt Domains

**Test Date:** October 16, 2025  
**Purpose:** Identify all possible WHOIS fields to capture in v1.1 implementation

---

## Test Results: 4 Domains Compared

### 1. debesyla.lt (Privacy Protected)
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
**Fields:** 9 data lines | NO contact organization | NO contact email

---

### 2. lrv.lt (Government - Public Contact)
```
Domain:                 lrv.lt
Status:                 registered
Registered:             2002-05-14
Expires:                2026-05-14
%
Registrar:              Kertinis valstybės telekomunikacijų centras
Registrar website:      https://kvtc.lrv.lt
Registrar email:        hostmaster@kvtc.gov.lt
%
Contact organization:   Lietuvos Respublikos Vyriausybes kanceliarija
Contact email:          p.ramoska@lrv.lt
%
Nameserver:             diana.ns.cloudflare.com
Nameserver:             johnny.ns.cloudflare.com
```
**Fields:** 11 data lines | ✅ Contact organization | ✅ Contact email

---

### 3. delfi.lt (Major News Portal)
```
Domain:                 delfi.lt
Status:                 registered
Registered:             1999-09-13
Expires:                2026-09-13
%
Registrar:              Telia Lietuva, AB
Registrar website:      http://www.hostex.lt
Registrar email:        domains@hostex.lt
%
Nameserver:             ns1.delfi.lt    [91.234.200.251]
Nameserver:             ns2.domreg.lt
Nameserver:             ns2.delfi.lt    [91.234.200.252]
```
**Fields:** 10 data lines | NO contact info | ✅ Nameserver IPs shown (bonus!)

---

### 4. vz.lt (Business)
```
Domain:                 vz.lt
Status:                 registered
Registered:             1999-01-25
Expires:                2026-01-25
%
Registrar:              UAB "Interneto vizija"
Registrar website:      https://www.iv.lt/
Registrar email:        hostmaster@iv.lt
%
Contact organization:   UAB "Interneto vizija"
Contact email:          hostmaster@iv.lt
%
Nameserver:             chloe.ns.cloudflare.com
Nameserver:             kayden.ns.cloudflare.com
```
**Fields:** 11 data lines | ✅ Contact organization | ✅ Contact email

---

## Complete Field Mapping

### Fields Present in ALL domains:
| Field | Example | Notes |
|-------|---------|-------|
| `Domain:` | `lrv.lt` | Domain name |
| `Status:` | `registered` | Registration status |
| `Registered:` | `2002-05-14` | Registration date (YYYY-MM-DD) |
| `Expires:` | `2026-05-14` | Expiration date (YYYY-MM-DD) |
| `Registrar:` | `Kertinis valstybės...` | Registrar name |
| `Registrar website:` | `https://kvtc.lrv.lt` | Registrar website URL |
| `Registrar email:` | `hostmaster@kvtc.gov.lt` | Registrar contact email |
| `Nameserver:` (multiple) | `diana.ns.cloudflare.com` | DNS nameservers (1-N) |

### Fields Present in SOME domains (optional):
| Field | Example | When Present |
|-------|---------|--------------|
| `Contact organization:` | `Lietuvos Respublikos...` | When NOT privacy protected |
| `Contact email:` | `p.ramoska@lrv.lt` | When NOT privacy protected |
| Nameserver IP | `[91.234.200.251]` | Sometimes included after nameserver |

### Fields NOT FOUND (but mentioned in original plan):
- ❌ `Updated:` - No "updated date" field found in any response
- ❌ `Registrant:` - No explicit registrant field (only "Contact organization")
- ❌ `Registry status codes` - Only simple "registered" status

---

## Privacy Protection Detection

**How to detect privacy protection:**
```python
if 'Contact organization:' not in whois_response:
    privacy_protected = True
else:
    privacy_protected = False
```

**Alternative check:**
```python
privacy_protected = 'Contact email:' not in whois_response
```

---

## Recommended Database Schema

### Option A: Flat Structure with Nulls (RECOMMENDED)
```sql
-- Add to domains table or create whois_data table
CREATE TABLE whois_data (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL REFERENCES domains(id),
    
    -- Core fields (always present if registered)
    status VARCHAR(50) NOT NULL,                    -- 'registered', 'available', etc.
    registered_date DATE,                           -- YYYY-MM-DD
    expires_date DATE,                              -- YYYY-MM-DD
    
    -- Registrar info (always present if registered)
    registrar_name VARCHAR(255),
    registrar_website VARCHAR(255),
    registrar_email VARCHAR(255),
    
    -- Contact info (NULL if privacy protected)
    contact_organization VARCHAR(255),              -- NULL = privacy protected
    contact_email VARCHAR(255),                     -- NULL = privacy protected
    
    -- Derived fields
    privacy_protected BOOLEAN DEFAULT TRUE,         -- Auto-detect from contact_organization
    domain_age_days INT,                            -- Calculated from registered_date
    days_until_expiry INT,                          -- Calculated from expires_date
    
    -- Technical
    nameservers TEXT[],                             -- Array of nameserver hostnames
    nameserver_ips JSONB,                           -- Optional: {"ns1.delfi.lt": "91.234.200.251"}
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT NOW(),
    raw_response TEXT                               -- Store full WHOIS response for debugging
);

CREATE INDEX idx_whois_domain ON whois_data(domain_id);
CREATE INDEX idx_whois_privacy ON whois_data(privacy_protected);
CREATE INDEX idx_whois_expiry ON whois_data(expires_date);
CREATE INDEX idx_whois_registrar ON whois_data(registrar_name);
```

### Option B: JSONB Structure (More Flexible)
```sql
-- Store in existing results.data JSONB column
{
    "whois": {
        "status": "registered",
        "dates": {
            "registered": "2002-05-14",
            "expires": "2026-05-14",
            "age_days": 8526
        },
        "registrar": {
            "name": "Kertinis valstybės...",
            "website": "https://kvtc.lrv.lt",
            "email": "hostmaster@kvtc.gov.lt"
        },
        "contact": {
            "organization": "Lietuvos Respublikos...",  // null if privacy protected
            "email": "p.ramoska@lrv.lt",                // null if privacy protected
            "privacy_protected": false
        },
        "nameservers": [
            "diana.ns.cloudflare.com",
            "johnny.ns.cloudflare.com"
        ],
        "raw_response": "% Hello, this is..."
    }
}
```

---

## Recommended Approach: **Option B (JSONB)**

**Why:**
1. ✅ No schema changes needed (use existing `results.data` column)
2. ✅ Flexible structure (easy to add fields later)
3. ✅ Already have JSONB infrastructure
4. ✅ Easy to query: `data->'whois'->'contact'->>'organization'`
5. ✅ Handles optional fields gracefully (null values)

**How to mark privacy-protected domains:**
```json
{
    "whois": {
        "contact": {
            "organization": null,
            "email": null,
            "privacy_protected": true
        }
    }
}
```

---

## Implementation Strategy for v1.1

### 1. Parse WHOIS Response
```python
def parse_whois_response(response: str) -> dict:
    """Parse .lt WHOIS response into structured data."""
    data = {
        'status': None,
        'registered': None,
        'expires': None,
        'registrar': {},
        'contact': {},
        'nameservers': [],
        'raw_response': response
    }
    
    for line in response.split('\n'):
        if line.startswith('%') or not line.strip():
            continue
        
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Core fields
        if key == 'Domain':
            data['domain'] = value
        elif key == 'Status':
            data['status'] = value
        elif key == 'Registered':
            data['registered'] = value
        elif key == 'Expires':
            data['expires'] = value
        
        # Registrar
        elif key == 'Registrar':
            data['registrar']['name'] = value
        elif key == 'Registrar website':
            data['registrar']['website'] = value
        elif key == 'Registrar email':
            data['registrar']['email'] = value
        
        # Contact (may be absent if privacy protected)
        elif key == 'Contact organization':
            data['contact']['organization'] = value
        elif key == 'Contact email':
            data['contact']['email'] = value
        
        # Nameservers
        elif key == 'Nameserver':
            # Handle optional IP: "ns1.delfi.lt    [91.234.200.251]"
            if '[' in value:
                ns_name, ns_ip = value.split('[')
                data['nameservers'].append({
                    'hostname': ns_name.strip(),
                    'ip': ns_ip.rstrip(']').strip()
                })
            else:
                data['nameservers'].append({
                    'hostname': value,
                    'ip': None
                })
    
    # Detect privacy protection
    data['contact']['privacy_protected'] = (
        'organization' not in data['contact'] or 
        data['contact'].get('organization') is None
    )
    
    # Calculate derived fields
    if data['registered']:
        from datetime import datetime
        reg_date = datetime.strptime(data['registered'], '%Y-%m-%d')
        data['age_days'] = (datetime.now() - reg_date).days
    
    if data['expires']:
        exp_date = datetime.strptime(data['expires'], '%Y-%m-%d')
        data['days_until_expiry'] = (exp_date - datetime.now()).days
    
    return data
```

### 2. Return Structure
```python
async def run_whois_check(domain: str, config: dict) -> dict:
    # ... existing DAS check ...
    
    if registered:
        # Query WHOIS for details
        whois_data = await whois_client.query(domain)
        parsed = parse_whois_response(whois_data)
        
        return {
            'status': 'registered',
            'registration': {
                'status': parsed['status'],
                'registered_date': parsed['registered'],
                'expires_date': parsed['expires'],
                'age_days': parsed['age_days'],
                'days_until_expiry': parsed['days_until_expiry']
            },
            'registrar': parsed['registrar'],
            'contact': parsed['contact'],
            'nameservers': [ns['hostname'] for ns in parsed['nameservers']],
            'technical': {
                'nameserver_details': parsed['nameservers']  # includes IPs
            },
            'raw_whois': parsed['raw_response']
        }
```

---

## Summary

### Fields to Capture (Priority Order):
1. ✅ **Domain** - domain name
2. ✅ **Status** - registered/available
3. ✅ **Registered date** - YYYY-MM-DD
4. ✅ **Expires date** - YYYY-MM-DD
5. ✅ **Registrar name**
6. ✅ **Registrar website**
7. ✅ **Registrar email**
8. ✅ **Contact organization** (NULL if privacy protected)
9. ✅ **Contact email** (NULL if privacy protected)
10. ✅ **Privacy protected flag** (derived from contact presence)
11. ✅ **Nameservers** (array)
12. ✅ **Domain age** (calculated)
13. ✅ **Days until expiry** (calculated)
14. ⭐ **Nameserver IPs** (bonus - when available)

### NOT Available (remove from plan):
- ❌ Updated date
- ❌ IANA registrar ID
- ❌ Registrant organization (use "Contact organization" instead)
- ❌ Registry status codes (only have "registered")

### Storage Recommendation:
**Use JSONB in `results.data` column** - no schema changes needed!

---

**Ready to implement v1.1 with this structure?** 🚀
