"""
Domain Utilities for v0.9 - Smart Redirect Capture

This module provides intelligent domain extraction and handling for the
redirect capture system. It handles:

1. Smart subdomain extraction (keep gov.lt, strip others)
2. Lithuanian domain detection (.lt TLD)
3. Domain capture eligibility (ignore common services)
4. Same domain family detection (www variants, etc.)

Key Functions:
- extract_main_domain(): Extract main domain with smart subdomain handling
- is_lithuanian_domain(): Check if domain is .lt
- should_capture_domain(): Determine if domain should be captured
- is_same_domain_family(): Check if two domains are the same (www, protocol)

Special Cases:
- .gov.lt domains: Keep subdomains (stat.gov.lt ≠ lrv.gov.lt)
- .lrv.lt domains: Keep subdomains (government agencies)
- Common services: Ignore (google.lt, facebook.com, etc.)
"""

from urllib.parse import urlparse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Patterns where we should keep the full subdomain
# These are special cases where subdomain matters (government, education, etc.)
KEEP_SUBDOMAIN_PATTERNS = [
    '.gov.lt',  # Government agencies (stat.gov.lt, lrv.gov.lt are different)
    '.lrv.lt',  # Lithuanian government
    '.edu.lt',  # Educational institutions
    '.mil.lt',  # Military
]

# Target TLDs to capture
TARGET_TLDS = ['.lt']

# Common services to ignore (not useful to capture)
IGNORE_DOMAINS = [
    # Lithuanian services
    'google.lt',
    'maps.google.lt',
    
    # International services (common Lithuanian usage)
    'facebook.com',
    'youtube.com',
    'linkedin.com',
    'twitter.com',
    'instagram.com',
    'google.com',
    'googleapis.com',
    'gstatic.com',
    'cloudflare.com',
    'cloudfront.net',
    'amazonaws.com',
]


def extract_main_domain(
    url: str,
    keep_patterns: Optional[List[str]] = None
) -> str:
    """
    Extract main domain from URL with intelligent subdomain handling.
    
    Rules:
    1. For .gov.lt, .lrv.lt, etc.: Keep full subdomain
    2. For regular .lt domains: Strip to root (blog.example.lt → example.lt)
    3. Remove www prefix in all cases
    4. Handle protocols, ports, paths
    
    Examples:
        https://www.example.lt/path → example.lt
        http://blog.example.lt → example.lt
        https://stat.gov.lt → stat.gov.lt (kept!)
        http://www.lrv.gov.lt → lrv.gov.lt (kept!)
        subdomain.deep.example.lt → example.lt
    
    Args:
        url: URL or domain string
        keep_patterns: List of patterns to keep subdomains for
                      (default: KEEP_SUBDOMAIN_PATTERNS)
    
    Returns:
        Extracted main domain
    """
    if keep_patterns is None:
        keep_patterns = KEEP_SUBDOMAIN_PATTERNS
    
    # Parse URL to extract hostname
    if '://' not in url:
        url = f'http://{url}'  # Add protocol for parsing
    
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.path.split('/')[0]
    
    if not hostname:
        return url
    
    hostname = hostname.lower()
    
    # Remove www prefix first
    if hostname.startswith('www.'):
        hostname = hostname[4:]
    
    # Check if we should keep the full subdomain
    for pattern in keep_patterns:
        if hostname.endswith(pattern):
            # Keep full domain for special cases
            logger.debug(f"Keeping full domain for special pattern: {hostname}")
            return hostname
    
    # For regular domains, strip to root domain (last 2 parts)
    parts = hostname.split('.')
    
    if len(parts) >= 2:
        # Keep only domain.tld (last 2 parts)
        root_domain = '.'.join(parts[-2:])
        
        if root_domain != hostname:
            logger.debug(f"Stripped subdomain: {hostname} → {root_domain}")
        
        return root_domain
    
    return hostname


def is_lithuanian_domain(domain: str) -> bool:
    """
    Check if domain is a Lithuanian domain (.lt TLD).
    
    Args:
        domain: Domain name or URL
    
    Returns:
        True if .lt domain, False otherwise
    
    Examples:
        example.lt → True
        https://example.lt → True
        example.com → False
        example.lt.com → False (must end with .lt)
    """
    # Extract domain if URL provided
    if '://' in domain:
        parsed = urlparse(domain)
        domain = parsed.hostname or domain
    
    domain = domain.lower().strip()
    
    # Remove trailing slash/path if present
    if '/' in domain:
        domain = domain.split('/')[0]
    
    return domain.endswith('.lt')


def should_capture_domain(
    source_domain: str,
    target_domain: str,
    ignore_list: Optional[List[str]] = None
) -> bool:
    """
    Determine if target domain should be captured from redirect.
    
    Rules:
    1. Must be .lt domain (Lithuanian)
    2. Must be different from source (no self-redirects)
    3. Must not be in ignore list (common services)
    4. Must not be same domain family (www variants)
    
    Args:
        source_domain: Original domain being analyzed
        target_domain: Redirect target domain
        ignore_list: List of domains to ignore (default: IGNORE_DOMAINS)
    
    Returns:
        True if should capture, False otherwise
    
    Examples:
        (example.lt, partner.lt) → True (capture!)
        (example.lt, example.lt) → False (same domain)
        (example.lt, www.example.lt) → False (same family)
        (example.lt, google.lt) → False (in ignore list)
        (example.lt, partner.com) → False (not .lt)
    """
    if ignore_list is None:
        ignore_list = IGNORE_DOMAINS
    
    # Normalize domains for comparison
    source_normalized = extract_main_domain(source_domain)
    target_normalized = extract_main_domain(target_domain)
    
    # Same domain - don't capture
    if source_normalized == target_normalized:
        logger.debug(f"Same domain, skipping: {source_normalized} == {target_normalized}")
        return False
    
    # Not Lithuanian - don't capture
    if not is_lithuanian_domain(target_normalized):
        logger.debug(f"Not .lt domain, skipping: {target_normalized}")
        return False
    
    # In ignore list - don't capture
    if target_normalized in ignore_list:
        logger.debug(f"In ignore list, skipping: {target_normalized}")
        return False
    
    # Passed all checks - capture it!
    logger.debug(f"Should capture: {target_normalized} (from {source_normalized})")
    return True


def is_same_domain_family(domain1: str, domain2: str) -> bool:
    """
    Check if two domains are the same family (ignoring www, protocol, case).
    
    This is used to detect same-domain redirects like:
    - example.lt → www.example.lt (same family)
    - example.lt → https://example.lt (same family)
    - example.lt → blog.example.lt (different - subdomain matters)
    
    Args:
        domain1: First domain or URL
        domain2: Second domain or URL
    
    Returns:
        True if same domain family, False otherwise
    
    Examples:
        (example.lt, www.example.lt) → True
        (example.lt, https://example.lt) → True
        (example.lt, EXAMPLE.LT) → True
        (example.lt, blog.example.lt) → False
        (example.lt, other.lt) → False
    """
    # Extract and normalize both domains
    norm1 = extract_main_domain(domain1)
    norm2 = extract_main_domain(domain2)
    
    return norm1.lower() == norm2.lower()


def extract_lt_domains_from_chain(
    redirect_chain: List[str],
    original_domain: str,
    ignore_list: Optional[List[str]] = None
) -> List[str]:
    """
    Extract capturable .lt domains from a redirect chain.
    
    Applies all capture rules:
    - Only .lt domains
    - Not the original domain
    - Not in ignore list
    - Smart subdomain handling
    - No duplicates
    
    Args:
        redirect_chain: List of URLs in redirect chain
        original_domain: Original domain being analyzed
        ignore_list: Domains to ignore (default: IGNORE_DOMAINS)
    
    Returns:
        List of unique .lt domains to capture
    
    Example:
        chain = ['https://example.lt', 'https://partner.lt', 'https://google.com']
        original = 'example.lt'
        → ['partner.lt']
    """
    if ignore_list is None:
        ignore_list = IGNORE_DOMAINS
    
    captured = set()
    
    for url in redirect_chain:
        # Extract domain from URL
        domain = extract_main_domain(url)
        
        # Check if should capture
        if should_capture_domain(original_domain, domain, ignore_list):
            captured.add(domain)
    
    result = sorted(list(captured))
    
    if result:
        logger.info(f"Captured {len(result)} domain(s) from redirect chain: {result}")
    
    return result


def get_domain_from_url(url: str) -> str:
    """
    Extract just the domain/hostname from a URL.
    
    Args:
        url: URL string
    
    Returns:
        Domain/hostname
    
    Examples:
        https://example.lt/path → example.lt
        http://www.example.lt:8080 → www.example.lt
        example.lt → example.lt
    """
    if '://' not in url:
        url = f'http://{url}'
    
    parsed = urlparse(url)
    return parsed.hostname or url


# Export key functions
__all__ = [
    'extract_main_domain',
    'is_lithuanian_domain',
    'should_capture_domain',
    'is_same_domain_family',
    'extract_lt_domains_from_chain',
    'get_domain_from_url',
    'KEEP_SUBDOMAIN_PATTERNS',
    'TARGET_TLDS',
    'IGNORE_DOMAINS',
]
