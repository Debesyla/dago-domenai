"""
Profile schema definitions and validation for composable domain analysis.

v0.10 - Composable Profile System

This module defines the structure and validation for analysis profiles.
Profiles are organized by data source (dns, http, ssl, whois) rather than
scan depth (basic, full), enabling efficient data reuse and flexible combinations.
"""

from typing import Dict, List, Optional, Set, Any
from enum import Enum


class ProfileCategory(Enum):
    """Profile categories based on their purpose."""
    CORE = "core"  # Core data retrieval (dns, http, ssl, whois)
    ANALYSIS = "analysis"  # Data analysis (headers, content, infrastructure)
    INTELLIGENCE = "intelligence"  # Business insights (security, compliance, seo)
    META = "meta"  # Pre-configured combinations (quick-check, standard, complete)


class ProfileType(Enum):
    """Known profile types."""
    # Core Data Profiles
    QUICK_WHOIS = "quick-whois"
    WHOIS = "whois"
    DNS = "dns"
    HTTP = "http"
    SSL = "ssl"
    
    # Analysis Profiles
    HEADERS = "headers"
    CONTENT = "content"
    INFRASTRUCTURE = "infrastructure"
    TECHNOLOGY = "technology"
    SEO = "seo"
    
    # Intelligence Profiles
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS = "business"
    LANGUAGE = "language"
    FINGERPRINTING = "fingerprinting"
    CLUSTERING = "clustering"
    
    # Meta Profiles
    QUICK_CHECK = "quick-check"
    STANDARD = "standard"
    TECHNICAL_AUDIT = "technical-audit"
    BUSINESS_RESEARCH = "business-research"
    COMPLETE = "complete"
    MONITOR = "monitor"


# Profile dependency graph
PROFILE_DEPENDENCIES: Dict[str, List[str]] = {
    # Core profiles have no dependencies
    'quick-whois': [],
    'whois': [],
    'dns': [],
    'http': [],
    'ssl': [],
    
    # Analysis profiles depend on core profiles
    'headers': ['http'],
    'content': ['http'],
    'infrastructure': ['dns', 'http'],
    'technology': ['http', 'content'],
    'seo': ['http', 'content'],
    
    # Intelligence profiles have complex dependencies
    'security': ['http', 'headers', 'ssl'],
    'compliance': ['http', 'content', 'headers'],
    'business': ['whois', 'http', 'content'],
    'language': ['http', 'content'],
    'fingerprinting': ['http', 'content'],
    'clustering': ['dns', 'whois'],
    
    # Meta profiles expand to other profiles
    'quick-check': ['quick-whois', 'http'],
    'standard': ['whois', 'dns', 'http', 'ssl', 'seo'],
    'technical-audit': ['whois', 'dns', 'http', 'ssl', 'headers', 'security', 'infrastructure', 'technology'],
    'business-research': ['whois', 'dns', 'http', 'ssl', 'business', 'language', 'clustering'],
    'complete': ['whois', 'dns', 'http', 'ssl', 'headers', 'content', 'infrastructure', 
                 'technology', 'seo', 'security', 'compliance', 'business', 'language'],
    'monitor': ['quick-whois', 'http'],
}


# Profile metadata
PROFILE_METADATA: Dict[str, Dict[str, Any]] = {
    'quick-whois': {
        'category': ProfileCategory.CORE,
        'description': 'Fast registration status check (DAS protocol only)',
        'data_source': 'das.domreg.lt:4343 (DAS protocol)',
        'api_calls': 1,
        'duration_estimate': '0.02s',
        'rate_limit': '4 queries/sec',
        'use_cases': [
            'Bulk domain validation (10,000+ domains)',
            'Continuous monitoring',
            'Quick availability checks',
            'Initial domain filtering'
        ],
        'data_returned': [
            'Registration status (registered/available)',
            'Domain name',
            'Query metadata'
        ],
        'notes': 'Ultra-fast, no rate limit concerns. Use "whois" profile for complete registration data.'
    },
    'whois': {
        'category': ProfileCategory.CORE,
        'description': 'Complete domain registration data (DAS + WHOIS port 43)',
        'data_source': 'das.domreg.lt:4343 + whois.domreg.lt:43',
        'api_calls': 2,
        'duration_estimate': '0.10s',
        'rate_limit': '100 queries/30min (strict)',
        'use_cases': [
            'Deep domain research',
            'Registration detail analysis',
            'Contact information lookup',
            'Registrar verification'
        ],
        'data_returned': [
            'Registration status',
            'Registrar information',
            'Registration/expiry dates',
            'Nameservers',
            'Contact details (if public)',
            'Domain holder information'
        ],
        'notes': 'Strict rate limiting enforced. Falls back to DAS data if rate limited.'
    },
    'dns': {
        'category': ProfileCategory.CORE,
        'description': 'DNS resolution and all record types',
        'data_source': 'DNS servers',
        'api_calls': 1,  # Single query set returns A, AAAA, MX, NS, TXT, CNAME
        'duration_estimate': '0.3-0.8s',
    },
    'http': {
        'category': ProfileCategory.CORE,
        'description': 'HTTP connectivity, redirects, and response behavior',
        'data_source': 'HTTP/HTTPS requests',
        'api_calls': 2,  # HTTP + HTTPS
        'duration_estimate': '1-3s',
    },
    'ssl': {
        'category': ProfileCategory.CORE,
        'description': 'SSL/TLS certificate analysis',
        'data_source': 'TLS handshake',
        'api_calls': 1,
        'duration_estimate': '0.5-1.5s',
    },
    'headers': {
        'category': ProfileCategory.ANALYSIS,
        'description': 'HTTP header analysis for security and configuration',
        'data_source': 'HTTP response headers',
        'api_calls': 0,  # Reuses http data
        'duration_estimate': '<0.1s',
    },
    'content': {
        'category': ProfileCategory.ANALYSIS,
        'description': 'On-page content extraction and analysis',
        'data_source': 'HTML parsing',
        'api_calls': 0,  # Reuses http data
        'duration_estimate': '0.2-0.5s',
    },
    'infrastructure': {
        'category': ProfileCategory.ANALYSIS,
        'description': 'Hosting, CDN, and geolocation analysis',
        'data_source': 'DNS + HTTP data',
        'api_calls': 0,  # Reuses dns + http data
        'duration_estimate': '0.1-0.3s',
    },
    'technology': {
        'category': ProfileCategory.ANALYSIS,
        'description': 'Tech stack detection',
        'data_source': 'HTTP headers + HTML',
        'api_calls': 0,
        'duration_estimate': '0.1-0.3s',
    },
    'seo': {
        'category': ProfileCategory.ANALYSIS,
        'description': 'SEO checks',
        'data_source': 'HTTP + HTML',
        'api_calls': 0,
        'duration_estimate': '0.2-0.5s',
    },
    'security': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'Vulnerability scans and security analysis',
        'data_source': 'HTTP + headers + SSL',
        'api_calls': 0,
        'duration_estimate': '0.3-1s',
    },
    'compliance': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'GDPR and privacy checks',
        'data_source': 'HTTP + content + headers',
        'api_calls': 0,
        'duration_estimate': '0.2-0.5s',
    },
    'business': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'Company information and contacts',
        'data_source': 'WHOIS + HTTP + content',
        'api_calls': 0,
        'duration_estimate': '0.2-0.5s',
    },
    'language': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'Language detection and targeting',
        'data_source': 'HTTP + content',
        'api_calls': 0,
        'duration_estimate': '0.1-0.3s',
    },
    'fingerprinting': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'Screenshots and hashes',
        'data_source': 'HTTP + content',
        'api_calls': 1,  # May need screenshot service
        'duration_estimate': '2-5s',
    },
    'clustering': {
        'category': ProfileCategory.INTELLIGENCE,
        'description': 'Portfolio detection',
        'data_source': 'DNS + WHOIS',
        'api_calls': 0,
        'duration_estimate': '0.1-0.3s',
    },
    'quick-check': {
        'category': ProfileCategory.META,
        'description': 'Ultra-fast domain validation (status + connectivity)',
        'profiles': ['quick-whois', 'http'],
        'duration_estimate': '0.10-0.50s',
        'use_cases': [
            'Bulk domain screening (10,000+ domains)',
            'New domain discovery',
            'Quick validation',
            'Initial filtering before deep analysis'
        ],
        'notes': '12x faster than previous version. No rate limiting concerns.'
    },
    'standard': {
        'category': ProfileCategory.META,
        'description': 'General analysis (core profiles + seo)',
        'profiles': ['whois', 'dns', 'http', 'ssl', 'seo'],
        'duration_estimate': '3-7s',
    },
    'technical-audit': {
        'category': ProfileCategory.META,
        'description': 'Security and infrastructure focus',
        'profiles': ['whois', 'dns', 'http', 'ssl', 'headers', 'security', 'infrastructure', 'technology'],
        'duration_estimate': '4-9s',
    },
    'business-research': {
        'category': ProfileCategory.META,
        'description': 'Market intelligence',
        'profiles': ['whois', 'dns', 'http', 'ssl', 'business', 'language', 'clustering'],
        'duration_estimate': '4-8s',
    },
    'complete': {
        'category': ProfileCategory.META,
        'description': 'Comprehensive analysis (all checks)',
        'profiles': ['whois', 'dns', 'http', 'ssl', 'headers', 'content', 'infrastructure',
                    'technology', 'seo', 'security', 'compliance', 'business', 'language'],
        'duration_estimate': '6-15s',
    },
    'monitor': {
        'category': ProfileCategory.META,
        'description': 'Lightweight continuous monitoring (status + connectivity)',
        'profiles': ['quick-whois', 'http'],
        'duration_estimate': '0.10-0.50s',
        'use_cases': [
            'Continuous monitoring',
            'Status tracking',
            'Availability alerts',
            'Change detection'
        ],
        'notes': 'Optimized for frequent checks with minimal overhead.'
    },
}


def validate_profile_name(profile: str) -> bool:
    """
    Validate that a profile name is known.
    
    Args:
        profile: Profile name to validate
        
    Returns:
        True if profile is valid, False otherwise
    """
    return profile in PROFILE_DEPENDENCIES


def get_profile_category(profile: str) -> Optional[ProfileCategory]:
    """
    Get the category for a profile.
    
    Args:
        profile: Profile name
        
    Returns:
        ProfileCategory or None if profile not found
    """
    metadata = PROFILE_METADATA.get(profile)
    return metadata.get('category') if metadata else None


def get_profile_dependencies(profile: str) -> List[str]:
    """
    Get direct dependencies for a profile.
    
    Args:
        profile: Profile name
        
    Returns:
        List of profile names that this profile depends on
    """
    return PROFILE_DEPENDENCIES.get(profile, [])


def is_core_profile(profile: str) -> bool:
    """
    Check if a profile is a core data retrieval profile.
    
    Core profiles make external API calls: whois, dns, http, ssl
    
    Args:
        profile: Profile name
        
    Returns:
        True if core profile, False otherwise
    """
    category = get_profile_category(profile)
    return category == ProfileCategory.CORE if category else False


def is_meta_profile(profile: str) -> bool:
    """
    Check if a profile is a meta profile (expands to other profiles).
    
    Meta profiles: quick-check, standard, technical-audit, business-research, complete, monitor
    
    Args:
        profile: Profile name
        
    Returns:
        True if meta profile, False otherwise
    """
    category = get_profile_category(profile)
    return category == ProfileCategory.META if category else False


def get_all_profiles() -> List[str]:
    """
    Get list of all available profiles.
    
    Returns:
        List of all profile names
    """
    return list(PROFILE_DEPENDENCIES.keys())


def get_core_profiles() -> List[str]:
    """
    Get list of core data retrieval profiles.
    
    Returns:
        List of core profile names (whois, dns, http, ssl)
    """
    return [p for p in PROFILE_DEPENDENCIES.keys() if is_core_profile(p)]


def get_meta_profiles() -> List[str]:
    """
    Get list of meta profiles.
    
    Returns:
        List of meta profile names
    """
    return [p for p in PROFILE_DEPENDENCIES.keys() if is_meta_profile(p)]


def estimate_duration(profiles: List[str]) -> str:
    """
    Estimate total duration for a set of profiles.
    
    Note: This is a rough estimate. Actual duration depends on network,
    domain configuration, and parallelization.
    
    Args:
        profiles: List of profile names
        
    Returns:
        Duration estimate string (e.g., "3-7s")
    """
    # For now, return a simple estimate
    # TODO: Implement more sophisticated estimation based on profile composition
    core_count = sum(1 for p in profiles if is_core_profile(p))
    if core_count <= 1:
        return "0.5-2s"
    elif core_count == 2:
        return "1.5-4s"
    elif core_count <= 4:
        return "3-7s"
    else:
        return "4-10s"


def get_profile_info(profile: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a profile.
    
    Args:
        profile: Profile name
        
    Returns:
        Dictionary with profile metadata or None if not found
    """
    return PROFILE_METADATA.get(profile)
