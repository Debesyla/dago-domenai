"""
Active Status Check (v0.8.2 / Enhanced in v0.9)

Determines if a domain has an active website through:
- DNS resolution check
- HTTP/HTTPS connectivity test
- Redirect chain analysis
- Same-domain vs cross-domain detection
- .lt domain capture from redirect chains (v0.9: smart subdomain handling)

Active domains:
- Respond with 2xx/4xx status codes
- Redirect to same domain (www, https upgrades)

Inactive domains:
- No DNS resolution
- Connection timeout/refused
- 5xx server errors
- Redirect to different domain (parking/forwarding)

v0.9 Enhancements:
- Smart subdomain handling (.gov.lt subdomains preserved)
- Ignore list for common services
- Configurable capture rules
"""

import asyncio
import socket
import time
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse
import logging

# v0.9: Use centralized domain utilities
from src.utils.domain_utils import (
    extract_main_domain,
    is_lithuanian_domain,
    should_capture_domain,
    is_same_domain_family,
    extract_lt_domains_from_chain as extract_lt_domains_v09,
    get_domain_from_url
)

logger = logging.getLogger(__name__)


# Backward compatibility: Keep old function names as aliases
def extract_root_domain(domain: str) -> str:
    """
    DEPRECATED: Use domain_utils.extract_main_domain() instead.
    Kept for backward compatibility.
    """
    return extract_main_domain(domain)


def normalize_domain(domain: str) -> str:
    """
    Normalize domain for comparison (remove protocol, lowercase, remove www).
    
    v0.9: Now uses domain_utils for consistency.
    """
    return extract_main_domain(domain)


def is_same_domain(domain1: str, domain2: str) -> bool:
    """
    Check if two domains are the same (ignoring www, protocol, case).
    
    v0.9: Now uses domain_utils.is_same_domain_family() for consistency.
    
    www is treated as equivalent to no www, but other subdomains are NOT.
    
    Examples:
        example.lt == www.example.lt → True
        example.lt == https://example.lt → True
        example.lt == subdomain.example.lt → False (different subdomain)
        example.lt == other.lt → False
        subdomain.example.lt == www.subdomain.example.lt → True
    
    Args:
        domain1: First domain
        domain2: Second domain
    
    Returns:
        True if same domain, False otherwise
    """
    return is_same_domain_family(domain1, domain2)


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.
    
    v0.9: Now uses domain_utils.get_domain_from_url() for consistency.
    
    Args:
        url: Full URL
    
    Returns:
        Domain only
    """
    return get_domain_from_url(url)


def extract_lt_domains_from_chain(
    redirect_chain: List[str], 
    original_domain: str,
    config: Dict[str, Any] = None
) -> List[str]:
    """
    Extract all .lt domains from redirect chain (v0.9: smart subdomain handling).
    
    v0.9 Enhancements:
    - Uses domain_utils for smart subdomain handling
    - Preserves .gov.lt, .lrv.lt subdomains
    - Applies ignore list for common services
    - Configurable via config.yaml
    
    Rules:
    - Only capture .lt domains
    - Smart subdomain handling (keep gov.lt, strip others)
    - Exclude the original domain
    - Apply ignore list
    - Remove duplicates
    
    Args:
        redirect_chain: List of URLs in redirect chain
        original_domain: Original domain being checked (to exclude)
        config: Optional configuration dict (for ignore list)
    
    Returns:
        List of captured .lt domains
    """
    # Get configuration
    ignore_list = None
    if config:
        capture_config = config.get('redirect_capture', {})
        if capture_config.get('enabled', True):
            ignore_list = capture_config.get('ignore_common_services')
    
    # Use v0.9 domain_utils function
    return extract_lt_domains_v09(redirect_chain, original_domain, ignore_list)


async def check_dns_resolution(domain: str) -> bool:
    """
    Check if domain has DNS resolution.
    
    Args:
        domain: Domain to check
    
    Returns:
        True if DNS resolves, False otherwise
    """
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, socket.gethostbyname, domain)
        return True
    except (socket.gaierror, socket.herror):
        return False
    except Exception as e:
        logger.debug(f"DNS check failed for {domain}: {e}")
        return False


async def check_http_connectivity(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Check HTTP/HTTPS connectivity with HEAD request.
    
    Uses HEAD request for speed (no body download).
    Tries HTTPS first, falls back to HTTP.
    Follows redirects and tracks chain.
    
    Args:
        domain: Domain to check
        timeout: Request timeout in seconds
    
    Returns:
        {
            'success': bool,
            'status_code': int,
            'final_url': str,
            'redirect_chain': list,
            'error': str
        }
    """
    try:
        import aiohttp
        
        # Try HTTPS first
        urls_to_try = [
            f"https://{domain}",
            f"http://{domain}"
        ]
        
        for url in urls_to_try:
            try:
                async with aiohttp.ClientSession() as session:
                    redirect_chain = []
                    
                    async with session.head(
                        url,
                        allow_redirects=True,
                        timeout=aiohttp.ClientTimeout(total=timeout),
                        ssl=False  # Don't fail on SSL errors
                    ) as response:
                        # Track redirect chain
                        if response.history:
                            redirect_chain = [str(r.url) for r in response.history]
                        redirect_chain.append(str(response.url))
                        
                        return {
                            'success': True,
                            'status_code': response.status,
                            'final_url': str(response.url),
                            'redirect_chain': redirect_chain,
                            'protocol': 'https' if url.startswith('https') else 'http'
                        }
            
            except asyncio.TimeoutError:
                continue  # Try next protocol
            except aiohttp.ClientError:
                continue  # Try next protocol
        
        # Both protocols failed
        return {
            'success': False,
            'error': 'Connection failed on both HTTP and HTTPS'
        }
    
    except ImportError:
        # Fallback: use requests library (synchronous)
        import requests
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _check_http_sync,
            domain,
            timeout
        )
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def _check_http_sync(domain: str, timeout: float) -> Dict[str, Any]:
    """
    Synchronous HTTP check (fallback when aiohttp not available).
    
    Args:
        domain: Domain to check
        timeout: Request timeout
    
    Returns:
        Same format as check_http_connectivity
    """
    import requests
    
    urls_to_try = [
        f"https://{domain}",
        f"http://{domain}"
    ]
    
    for url in urls_to_try:
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=timeout,
                verify=False  # Don't fail on SSL errors
            )
            
            # Track redirect chain
            redirect_chain = []
            if response.history:
                redirect_chain = [r.url for r in response.history]
            redirect_chain.append(response.url)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'final_url': response.url,
                'redirect_chain': redirect_chain,
                'protocol': 'https' if url.startswith('https') else 'http'
            }
        
        except requests.Timeout:
            continue
        except requests.RequestException:
            continue
    
    return {
        'success': False,
        'error': 'Connection failed on both HTTP and HTTPS'
    }


async def run_active_check(
    domain: str,
    config: dict,
    status_result: Dict = None,
    redirect_result: Dict = None
) -> Dict[str, Any]:
    """
    Run comprehensive active check on domain.
    
    This is the v0.8.2 implementation with real DNS and HTTP checks.
    
    Determines if domain has active website through:
    1. DNS resolution check (fail-fast if no DNS)
    2. HTTP/HTTPS connectivity test
    3. Status code analysis (2xx/4xx = active, 5xx = inactive)
    4. Redirect chain analysis (same-domain = active, cross-domain = inactive)
    5. .lt domain capture from redirects
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary
        status_result: Result from status_check (optional, used as fallback)
        redirect_result: Result from redirect_check (optional, used as fallback)
    
    Returns:
        {
            'check': 'active',
            'domain': str,
            'active': bool,
            'reason': str,
            'has_dns': bool,
            'responds': bool,
            'status_code': int,
            'final_url': str,
            'redirect_chain': list,
            'captured_domains': list,  # New .lt domains discovered
            'meta': {
                'method': str,
                'execution_time': float
            }
        }
    """
    start_time = time.time()
    
    # Get timeout from config
    timeout = config.get('network', {}).get('request_timeout', 5.0)
    
    # Step 1: DNS Check (fail-fast)
    logger.debug(f"Checking DNS resolution for {domain}")
    has_dns = await check_dns_resolution(domain)
    
    if not has_dns:
        execution_time = time.time() - start_time
        return {
            'check': 'active',
            'domain': domain,
            'active': False,
            'reason': 'No DNS resolution',
            'has_dns': False,
            'responds': False,
            'captured_domains': [],
            'meta': {
                'method': 'DNS',
                'execution_time': execution_time
            }
        }
    
    # Step 2: HTTP/HTTPS Connectivity Check
    logger.debug(f"Checking HTTP connectivity for {domain}")
    http_result = await check_http_connectivity(domain, timeout)
    
    if not http_result.get('success'):
        execution_time = time.time() - start_time
        return {
            'check': 'active',
            'domain': domain,
            'active': False,
            'reason': http_result.get('error', 'Connection failed'),
            'has_dns': True,
            'responds': False,
            'captured_domains': [],
            'meta': {
                'method': 'HTTP',
                'execution_time': execution_time
            }
        }
    
    # Step 3: Analyze Response
    status_code = http_result.get('status_code', 0)
    final_url = http_result.get('final_url', '')
    redirect_chain = http_result.get('redirect_chain', [])
    
    # Step 4: Extract captured .lt domains from redirect chain
    captured_domains = list(extract_lt_domains_from_chain(redirect_chain, domain))
    
    if captured_domains:
        logger.info(f"📥 Captured {len(captured_domains)} .lt domain(s) from {domain}: {', '.join(captured_domains)}")
    
    # Step 5: Determine if active based on status code
    execution_time = time.time() - start_time
    
    # 5xx errors = inactive (server errors)
    if status_code >= 500:
        return {
            'check': 'active',
            'domain': domain,
            'active': False,
            'reason': f'Server error: HTTP {status_code}',
            'has_dns': True,
            'responds': True,
            'status_code': status_code,
            'final_url': final_url,
            'redirect_chain': redirect_chain,
            'captured_domains': captured_domains,
            'meta': {
                'method': 'HTTP',
                'execution_time': execution_time
            }
        }
    
    # 2xx/4xx = active (site exists, even if 404 on homepage)
    if status_code >= 200 and status_code < 500:
        # Check if redirected to different domain
        final_domain = extract_domain_from_url(final_url)
        
        if is_same_domain(domain, final_domain):
            # Same domain (with www, https, etc.) = ACTIVE
            return {
                'check': 'active',
                'domain': domain,
                'active': True,
                'reason': f'Active site - HTTP {status_code}',
                'has_dns': True,
                'responds': True,
                'status_code': status_code,
                'final_url': final_url,
                'redirect_chain': redirect_chain,
                'captured_domains': captured_domains,
                'meta': {
                    'method': 'HTTP',
                    'execution_time': execution_time
                }
            }
        else:
            # Different domain = INACTIVE (parked/forwarded)
            return {
                'check': 'active',
                'domain': domain,
                'active': False,
                'reason': f'Redirects to different domain: {final_domain}',
                'has_dns': True,
                'responds': True,
                'status_code': status_code,
                'final_url': final_url,
                'redirect_chain': redirect_chain,
                'captured_domains': captured_domains,
                'meta': {
                    'method': 'HTTP',
                    'execution_time': execution_time
                }
            }
    
    # Unknown status code = inactive (conservative)
    return {
        'check': 'active',
        'domain': domain,
        'active': False,
        'reason': f'Unknown status: HTTP {status_code}',
        'has_dns': True,
        'responds': True,
        'status_code': status_code,
        'final_url': final_url,
        'redirect_chain': redirect_chain,
        'captured_domains': captured_domains,
        'meta': {
            'method': 'HTTP',
            'execution_time': execution_time
        }
    }


async def check_domain_active(
    domain: str,
    config: dict,
    status_result: Dict = None,
    redirect_result: Dict = None
) -> bool:
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


def insert_captured_domains(db_url: str, captured_domains: List[str], source_domain: str):
    """
    Insert captured .lt domains into database for future checking.
    
    Args:
        db_url: Database connection URL
        captured_domains: List of captured .lt domains
        source_domain: Original domain that redirected (for logging)
    
    Returns:
        Number of newly inserted domains
    """
    if not captured_domains:
        return 0
    
    try:
        from src.utils.db import insert_captured_domain
        
        inserted_count = 0
        for domain in captured_domains:
            try:
                # insert_captured_domain returns True if new, False if exists
                if insert_captured_domain(db_url, domain, source_domain):
                    inserted_count += 1
            except Exception as e:
                logger.debug(f"Could not insert {domain}: {e}")
        
        if inserted_count > 0:
            logger.info(f"📥 Captured {inserted_count} new .lt domain(s) from {source_domain}")
        
        return inserted_count
    
    except ImportError:
        logger.warning("Could not import db module - captured domains not saved")
        return 0
    except Exception as e:
        logger.error(f"Error inserting captured domains: {e}")
        return 0


# Example usage and testing
if __name__ == "__main__":
    """
    Test active check implementation with sample domains.
    
    Usage:
        python -m src.checks.active_check
    """
    async def test_active_check():
        print("Testing Active Check Implementation (v0.8.2)")
        print("=" * 60)
        
        # Test domains with different scenarios
        test_cases = [
            ("google.lt", "Should be INACTIVE - redirects to google.com"),
            ("lrytas.lt", "Should be ACTIVE - major Lithuanian news site"),
            ("nonexistent-xyz-test-12345.lt", "Should be INACTIVE - no DNS"),
            ("delfi.lt", "Should be ACTIVE - major Lithuanian news site"),
        ]
        
        config = {'network': {'request_timeout': 5.0}}
        
        for domain, description in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {domain}")
            print(f"Expected: {description}")
            print(f"{'='*60}")
            
            result = await run_active_check(domain, config)
            
            print(f"Active: {result.get('active')}")
            print(f"Reason: {result.get('reason')}")
            print(f"Has DNS: {result.get('has_dns')}")
            print(f"Responds: {result.get('responds')}")
            
            if result.get('status_code'):
                print(f"Status Code: {result.get('status_code')}")
            
            if result.get('final_url'):
                print(f"Final URL: {result.get('final_url')}")
            
            if result.get('captured_domains'):
                print(f"Captured Domains: {', '.join(result.get('captured_domains'))}")
            
            print(f"Execution Time: {result.get('meta', {}).get('execution_time', 0):.2f}s")
        
        print(f"\n{'='*60}")
        print("Testing Domain Normalization Helpers")
        print(f"{'='*60}")
        
        # Test helper functions
        test_helpers = [
            ("www.example.lt", "example.lt", "extract_root_domain"),
            ("subdomain.example.lt", "example.lt", "extract_root_domain"),
            ("example.lt", "example.lt", "normalize_domain"),
            ("www.example.lt", "example.lt", "normalize_domain"),
        ]
        
        for input_domain, expected, func_name in test_helpers:
            if func_name == "extract_root_domain":
                result = extract_root_domain(input_domain)
            else:
                result = normalize_domain(input_domain)
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {func_name}('{input_domain}') = '{result}' (expected: '{expected}')")
        
        # Test same domain comparison
        print(f"\n{'='*60}")
        print("Testing Same Domain Comparison")
        print(f"{'='*60}")
        
        same_domain_tests = [
            ("example.lt", "www.example.lt", True),
            ("example.lt", "https://example.lt", True),
            ("example.lt", "http://www.example.lt", True),
            ("example.lt", "other.lt", False),
            ("example.lt", "subdomain.example.lt", False),
        ]
        
        for domain1, domain2, expected in same_domain_tests:
            result = is_same_domain(domain1, domain2)
            status = "✅" if result == expected else "❌"
            print(f"{status} is_same_domain('{domain1}', '{domain2}') = {result} (expected: {expected})")
    
    # Run the test
    asyncio.run(test_active_check())

