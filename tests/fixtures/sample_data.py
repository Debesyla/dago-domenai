"""Test fixtures and mock data

Provides reusable test data, mock objects, and helper functions.
"""
import json
from typing import Dict, Any


# Sample domain results
SAMPLE_SUCCESS_RESULT = {
    "domain": "example.com",
    "status": "success",
    "timestamp": "2025-10-15T10:00:00Z",
    "duration_ms": 1500,
    "checks": {
        "whois": {
            "status": "success",
            "duration_ms": 500,
            "data": {
                "registered": True,
                "registrar": "Example Registrar Inc.",
                "creation_date": "2000-01-01",
                "expiration_date": "2026-01-01",
                "nameservers": ["ns1.example.com", "ns2.example.com"],
            },
        },
        "http": {
            "status": "success",
            "duration_ms": 250,
            "data": {
                "status_code": 200,
                "response_time_ms": 250,
                "redirects": [],
                "final_url": "https://example.com/",
                "https": True,
            },
        },
        "ssl": {
            "status": "success",
            "duration_ms": 300,
            "data": {
                "valid": True,
                "issuer": "Let's Encrypt",
                "expiration_date": "2026-01-01",
                "days_until_expiry": 365,
            },
        },
    },
    "summary": {
        "grade": "A",
        "https_enabled": True,
        "reachable": True,
        "total_checks": 3,
        "successful_checks": 3,
        "failed_checks": 0,
    },
}


SAMPLE_PARTIAL_RESULT = {
    "domain": "partial-example.com",
    "status": "partial",
    "timestamp": "2025-10-15T10:00:00Z",
    "duration_ms": 2000,
    "checks": {
        "whois": {
            "status": "success",
            "duration_ms": 500,
            "data": {"registered": True},
        },
        "http": {
            "status": "error",
            "duration_ms": 1500,
            "error": "Connection timeout",
        },
    },
    "summary": {
        "grade": "C",
        "https_enabled": False,
        "reachable": False,
        "total_checks": 2,
        "successful_checks": 1,
        "failed_checks": 1,
    },
}


SAMPLE_ERROR_RESULT = {
    "domain": "error-example.com",
    "status": "error",
    "timestamp": "2025-10-15T10:00:00Z",
    "duration_ms": 100,
    "error": "Domain not registered",
    "checks": {},
    "summary": {
        "grade": "F",
        "https_enabled": False,
        "reachable": False,
        "total_checks": 0,
        "successful_checks": 0,
        "failed_checks": 0,
    },
}


# Sample check results
SAMPLE_WHOIS_DATA = {
    "registered": True,
    "registrar": "Test Registrar",
    "creation_date": "2010-01-01",
    "expiration_date": "2026-01-01",
    "updated_date": "2024-01-01",
    "nameservers": ["ns1.example.com", "ns2.example.com"],
    "status": ["clientTransferProhibited"],
}


SAMPLE_HTTP_DATA = {
    "status_code": 200,
    "response_time_ms": 150,
    "redirects": [
        {
            "from": "http://example.com",
            "to": "https://example.com",
            "status_code": 301,
        }
    ],
    "final_url": "https://example.com/",
    "https": True,
    "headers": {
        "Content-Type": "text/html; charset=utf-8",
        "Server": "nginx",
    },
}


SAMPLE_SSL_DATA = {
    "valid": True,
    "issuer": "Let's Encrypt Authority X3",
    "subject": "example.com",
    "expiration_date": "2026-01-01T00:00:00Z",
    "days_until_expiry": 365,
    "san": ["example.com", "www.example.com"],
    "protocol": "TLSv1.3",
}


SAMPLE_DNS_DATA = {
    "A": ["93.184.216.34"],
    "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"],
    "MX": [
        {"priority": 10, "host": "mail.example.com"},
        {"priority": 20, "host": "mail2.example.com"},
    ],
    "NS": ["ns1.example.com", "ns2.example.com"],
    "TXT": ["v=spf1 include:_spf.example.com ~all"],
}


# Profile execution plans
SAMPLE_EXECUTION_PLAN_SIMPLE = {
    "profiles": ["whois"],
    "execution_order": ["whois"],
    "parallel_groups": [["whois"]],
    "estimated_duration_s": 5,
}


SAMPLE_EXECUTION_PLAN_COMPLEX = {
    "profiles": ["technical-audit"],
    "execution_order": ["whois", "dns", "http", "ssl", "headers", "seo", "infrastructure", "security"],
    "parallel_groups": [
        ["whois", "dns"],
        ["http"],
        ["ssl", "headers"],
        ["seo", "infrastructure", "security"],
    ],
    "estimated_duration_s": 45,
}


# Helper functions
def get_sample_result(status: str = "success") -> Dict[str, Any]:
    """Get a sample result by status
    
    Args:
        status: Result status ("success", "partial", "error")
        
    Returns:
        Sample result dictionary
    """
    results = {
        "success": SAMPLE_SUCCESS_RESULT,
        "partial": SAMPLE_PARTIAL_RESULT,
        "error": SAMPLE_ERROR_RESULT,
    }
    return json.loads(json.dumps(results.get(status, SAMPLE_SUCCESS_RESULT)))


def get_sample_check_data(check_type: str) -> Dict[str, Any]:
    """Get sample check data by type
    
    Args:
        check_type: Check type ("whois", "http", "ssl", "dns")
        
    Returns:
        Sample check data dictionary
    """
    data = {
        "whois": SAMPLE_WHOIS_DATA,
        "http": SAMPLE_HTTP_DATA,
        "ssl": SAMPLE_SSL_DATA,
        "dns": SAMPLE_DNS_DATA,
    }
    return json.loads(json.dumps(data.get(check_type, {})))


def create_mock_database_response(rows: list) -> list:
    """Create mock database response
    
    Args:
        rows: List of tuples representing database rows
        
    Returns:
        Mock database response
    """
    return rows


# Test data sets
TEST_DOMAINS = [
    "example.com",
    "test.com",
    "sample.org",
    "demo.net",
]


TEST_ACTIVE_DOMAINS = [
    "google.com",
    "github.com",
    "python.org",
]


TEST_INACTIVE_DOMAINS = [
    "thisdoesnotexist-99999.invalid",
    "fake-domain-test-12345.com",
]


# Profile combinations for testing
TEST_PROFILE_COMBINATIONS = [
    ["whois"],
    ["whois", "http"],
    ["whois", "dns", "http", "ssl"],
    ["quick-check"],
    ["standard"],
    ["technical-audit"],
    ["complete"],
]


# Configuration variants
TEST_CONFIG_MINIMAL = {
    "checks": {
        "whois": {"enabled": True},
        "status": {"enabled": True},
    },
    "concurrency": {"max_workers": 1},
    "database": {"enabled": False},
}


TEST_CONFIG_FULL = {
    "checks": {
        "whois": {"enabled": True, "timeout": 10},
        "status": {"enabled": True, "timeout": 10},
        "redirect": {"enabled": True, "max_redirects": 5},
        "robots": {"enabled": True, "timeout": 10},
        "sitemap": {"enabled": True, "timeout": 10},
        "ssl": {"enabled": True, "timeout": 10},
    },
    "concurrency": {
        "max_workers": 10,
        "batch_size": 50,
    },
    "database": {
        "enabled": True,
        "url": "postgresql://localhost/dago_test",
    },
    "logging": {
        "level": "INFO",
        "format": "detailed",
    },
}
