"""
Active status check - Placeholder for v0.8
Real implementation in v0.8.2

This placeholder determines if a domain has an active website by combining
status and redirect check results.
"""

import asyncio
from typing import Dict, Any


async def run_active_check(domain: str, config: dict, status_result: Dict = None, redirect_result: Dict = None) -> Dict[str, Any]:
    """
    Placeholder active check - determines if domain is active.
    
    Real implementation in v0.8.2 will:
    - Combine HTTP status + redirect chain analysis
    - Check if domain redirects to itself (www variant, https upgrade) = ACTIVE
    - Check if domain redirects to different domain = INACTIVE
    - Check for 404, 403, 5xx errors = INACTIVE
    - Check for timeouts, connection errors = INACTIVE
    - Check for parked domain indicators = INACTIVE
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary
        status_result: Result from status_check (optional)
        redirect_result: Result from redirect_check (optional)
        
    Returns:
        Dictionary with activity status:
        {
            'active': True/False,
            'reason': str,
            'final_domain': str (optional),
            'error': str (optional)
        }
    """
    # Simulate check delay
    await asyncio.sleep(0.05)
    
    # Placeholder logic for v0.8
    # If we have status and redirect results, make basic determination
    if status_result and redirect_result:
        status_ok = status_result.get('ok', False)
        final_url = redirect_result.get('final_url', '')
        
        # Basic check: if status OK and not redirecting away
        if status_ok:
            # Extract domain from final URL
            if domain in final_url or final_url.replace('www.', '') == domain:
                return {
                    'active': True,
                    'reason': 'Domain responds with 2xx status',
                    'final_domain': domain,
                    'note': 'Placeholder check - real implementation in v0.8.2'
                }
            else:
                return {
                    'active': False,
                    'reason': f'Redirects to different domain: {final_url}',
                    'final_domain': final_url,
                    'note': 'Placeholder check - real implementation in v0.8.2'
                }
        else:
            return {
                'active': False,
                'reason': 'Domain not reachable or returns error',
                'note': 'Placeholder check - real implementation in v0.8.2'
            }
    
    # Default: assume active if no results provided
    result = {
        'active': True,
        'reason': 'No status/redirect data available - assumed active',
        'note': 'Placeholder check - real implementation in v0.8.2'
    }
    
    return result


async def check_domain_active(domain: str, config: dict, status_result: Dict = None, redirect_result: Dict = None) -> bool:
    """
    Convenience function to check if domain is active.
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary
        status_result: Result from status_check (optional)
        redirect_result: Result from redirect_check (optional)
        
    Returns:
        True if active, False otherwise
    """
    result = await run_active_check(domain, config, status_result, redirect_result)
    return result.get('active', False)


# For testing
if __name__ == '__main__':
    import sys
    
    test_domain = sys.argv[1] if len(sys.argv) > 1 else 'example.com'
    
    async def test():
        # Test with mock status/redirect results
        mock_status = {'ok': True, 'code': 200}
        mock_redirect = {'final_url': f'https://{test_domain}'}
        
        result = await run_active_check(test_domain, {}, mock_status, mock_redirect)
        print(f"Active check for {test_domain}:")
        print(f"  Active: {result['active']}")
        print(f"  Reason: {result['reason']}")
        print(f"  Note: {result.get('note', 'N/A')}")
    
    asyncio.run(test())
