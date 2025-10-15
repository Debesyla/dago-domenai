"""
WHOIS registration check - Placeholder for v0.8
Real implementation in v0.8.1

This placeholder always returns registered=True to allow testing
of the orchestrator's early bailout logic.
"""

import asyncio
from typing import Dict, Any


async def run_whois_check(domain: str, config: dict) -> Dict[str, Any]:
    """
    Placeholder WHOIS check - always returns registered=True.
    
    Real implementation in v0.8.1 will:
    - Query WHOIS servers via python-whois or socket
    - Parse registration status, registrar, expiration date
    - Handle rate limits and timeouts
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary
        
    Returns:
        Dictionary with registration status:
        {
            'registered': True/False,
            'registrar': str (optional),
            'expires_at': datetime (optional),
            'error': str (optional)
        }
    """
    # Simulate WHOIS query delay
    await asyncio.sleep(0.1)
    
    # Placeholder: assume all domains are registered
    # v0.8.1 will implement real WHOIS lookup
    result = {
        'registered': True,
        'registrar': 'Placeholder Registrar',
        'expires_at': None,
        'note': 'Placeholder check - real implementation in v0.8.1'
    }
    
    return result


async def check_domain_registration(domain: str, config: dict) -> bool:
    """
    Convenience function to check if domain is registered.
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary
        
    Returns:
        True if registered, False otherwise
    """
    result = await run_whois_check(domain, config)
    return result.get('registered', False)


# For testing
if __name__ == '__main__':
    import sys
    
    test_domain = sys.argv[1] if len(sys.argv) > 1 else 'example.com'
    
    async def test():
        result = await run_whois_check(test_domain, {})
        print(f"WHOIS check for {test_domain}:")
        print(f"  Registered: {result['registered']}")
        print(f"  Note: {result.get('note', 'N/A')}")
    
    asyncio.run(test())
