"""Pytest configuration and shared fixtures for dago-domenai tests"""
import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://localhost/dago_test")
TEST_DOMAIN = "example.com"
TEST_DOMAIN_ACTIVE = "google.com"
TEST_DOMAIN_INACTIVE = "thisdoesnotexist-99999.invalid"


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Load test configuration
    
    Returns a minimal valid config for testing
    """
    return {
        "checks": {
            "whois": {"enabled": True, "timeout": 5},
            "status": {"enabled": True, "timeout": 10},
            "redirect": {"enabled": True, "max_redirects": 5},
            "robots": {"enabled": True, "timeout": 10},
            "sitemap": {"enabled": True, "timeout": 10},
            "ssl": {"enabled": True, "timeout": 10},
        },
        "concurrency": {
            "max_workers": 2,
            "batch_size": 5,
        },
        "database": {
            "enabled": False,  # Disabled for unit tests
            "url": TEST_DATABASE_URL,
        },
        "logging": {
            "level": "ERROR",  # Quiet during tests
            "format": "minimal",
        },
    }


@pytest.fixture
def sample_domain() -> str:
    """Sample domain name for testing"""
    return TEST_DOMAIN


@pytest.fixture
def sample_active_domain() -> str:
    """Known active domain for integration tests"""
    return TEST_DOMAIN_ACTIVE


@pytest.fixture
def sample_inactive_domain() -> str:
    """Known inactive domain for testing"""
    return TEST_DOMAIN_INACTIVE


@pytest.fixture
def sample_domain_result() -> Dict[str, Any]:
    """Sample domain analysis result structure"""
    return {
        "domain": TEST_DOMAIN,
        "status": "success",
        "timestamp": "2025-10-15T10:00:00Z",
        "duration_ms": 1500,
        "checks": {
            "whois": {
                "status": "success",
                "data": {
                    "registered": True,
                    "registrar": "Example Registrar",
                    "creation_date": "2000-01-01",
                    "expiration_date": "2026-01-01",
                },
            },
            "http": {
                "status": "success",
                "data": {
                    "status_code": 200,
                    "response_time_ms": 250,
                    "redirects": [],
                },
            },
        },
        "summary": {
            "grade": "A",
            "https_enabled": True,
            "reachable": True,
            "total_checks": 2,
            "successful_checks": 2,
            "failed_checks": 0,
        },
    }


@pytest.fixture
def all_profile_names() -> list:
    """List of all profile names in the system"""
    return [
        # Core profiles (5)
        "quick-whois",
        "whois",
        "dns",
        "http",
        "ssl",
        # Analysis profiles
        "headers",
        "content",
        "infrastructure",
        "technology",
        "seo",
        # Intelligence profiles
        "security",
        "compliance",
        "business",
        "language",
        "fingerprinting",
        "clustering",
        # Meta profiles
        "quick-check",
        "standard",
        "technical-audit",
        "business-research",
        "complete",
        "monitor",
    ]


@pytest.fixture
def core_profile_names() -> list:
    """Core profile names"""
    return ["quick-whois", "whois", "dns", "http", "ssl"]


@pytest.fixture
def meta_profile_names() -> list:
    """Meta profile names"""
    return [
        "quick-check",
        "standard",
        "technical-audit",
        "business-research",
        "complete",
        "monitor",
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests requiring external services")
    config.addinivalue_line("markers", "db: Tests requiring database connection")
    config.addinivalue_line("markers", "slow: Slow tests that take >5 seconds")
    config.addinivalue_line("markers", "network: Tests requiring network access")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their location"""
    for item in items:
        # Auto-mark tests in unit/ directory
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Auto-mark tests in integration/ directory
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Auto-mark database tests
        if "db" in item.nodeid.lower() or "database" in item.nodeid.lower():
            item.add_marker(pytest.mark.db)
