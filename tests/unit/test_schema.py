"""Unit tests for core schema functions

Tests result structure creation, validation, and manipulation.
"""
import pytest
from src.core.schema import (
    new_domain_result,
    update_result_meta,
    add_check_result,
    update_summary,
)


class TestNewDomainResult:
    """Test creating new domain result structures"""

    def test_create_basic_result(self):
        """Test creating basic result structure"""
        result = new_domain_result("example.com", "test-task")
        
        assert result["domain"] == "example.com"
        assert result["task"] == "test-task"
        assert result["status"] == "pending"
        assert "timestamp" in result
        assert "checks" in result
        assert isinstance(result["checks"], dict)

    def test_result_has_required_fields(self):
        """Test that result has all required fields"""
        result = new_domain_result("example.com")
        
        required_fields = ["domain", "timestamp", "status", "checks", "summary"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_result_checks_is_empty_dict(self):
        """Test that checks starts as empty dict"""
        result = new_domain_result("example.com")
        assert result["checks"] == {}

    def test_result_with_custom_task(self):
        """Test creating result with custom task"""
        result = new_domain_result("example.com", task="custom-task")
        assert result["task"] == "custom-task"


class TestUpdateResultMeta:
    """Test updating result metadata"""

    def test_update_status(self):
        """Test updating result status"""
        result = new_domain_result("example.com")
        update_result_meta(result, status="success")
        
        assert result["status"] == "success"

    def test_update_duration(self):
        """Test updating duration"""
        result = new_domain_result("example.com")
        update_result_meta(result, duration_ms=1500)
        
        assert result["duration_ms"] == 1500

    def test_update_multiple_fields(self):
        """Test updating multiple metadata fields"""
        result = new_domain_result("example.com")
        update_result_meta(
            result,
            status="success",
            duration_ms=2000,
            profiles_executed=["whois", "http"]
        )
        
        assert result["status"] == "success"
        assert result["duration_ms"] == 2000
        assert result["profiles_executed"] == ["whois", "http"]

    def test_update_preserves_existing_data(self):
        """Test that updates preserve existing data"""
        result = new_domain_result("example.com")
        original_domain = result["domain"]
        
        update_result_meta(result, status="success")
        
        assert result["domain"] == original_domain


class TestAddCheckResult:
    """Test adding check results"""

    def test_add_successful_check(self):
        """Test adding successful check result"""
        result = new_domain_result("example.com")
        check_data = {
            "status": "success",
            "data": {"test": "value"},
            "duration_ms": 100,
        }
        
        add_check_result(result, "whois", check_data)
        
        assert "whois" in result["checks"]
        assert result["checks"]["whois"]["status"] == "success"

    def test_add_failed_check(self):
        """Test adding failed check result"""
        result = new_domain_result("example.com")
        check_data = {
            "status": "error",
            "error": "Connection timeout",
        }
        
        add_check_result(result, "http", check_data)
        
        assert "http" in result["checks"]
        assert result["checks"]["http"]["status"] == "error"

    def test_add_multiple_checks(self):
        """Test adding multiple check results"""
        result = new_domain_result("example.com")
        
        add_check_result(result, "whois", {"status": "success", "data": {}})
        add_check_result(result, "http", {"status": "success", "data": {}})
        add_check_result(result, "ssl", {"status": "success", "data": {}})
        
        assert len(result["checks"]) == 3
        assert "whois" in result["checks"]
        assert "http" in result["checks"]
        assert "ssl" in result["checks"]

    def test_overwrite_existing_check(self):
        """Test that adding check with same name overwrites"""
        result = new_domain_result("example.com")
        
        add_check_result(result, "whois", {"status": "pending", "data": {}})
        add_check_result(result, "whois", {"status": "success", "data": {"updated": True}})
        
        assert result["checks"]["whois"]["status"] == "success"
        assert result["checks"]["whois"]["data"]["updated"] is True


class TestUpdateSummary:
    """Test updating result summary"""

    def test_update_summary_basic(self):
        """Test basic summary update"""
        result = new_domain_result("example.com")
        result["checks"]["whois"] = {"status": "success"}
        result["checks"]["http"] = {"status": "success"}
        
        update_summary(result)
        
        assert "summary" in result
        summary = result["summary"]
        assert "total_checks" in summary
        assert summary["total_checks"] == 2

    def test_update_summary_with_failures(self):
        """Test summary with failed checks"""
        result = new_domain_result("example.com")
        result["checks"]["whois"] = {"status": "success"}
        result["checks"]["http"] = {"status": "error"}
        
        update_summary(result)
        
        summary = result["summary"]
        assert summary["successful_checks"] == 1
        assert summary["failed_checks"] == 1

    def test_update_summary_all_success(self):
        """Test summary with all successful checks"""
        result = new_domain_result("example.com")
        result["checks"]["whois"] = {"status": "success"}
        result["checks"]["http"] = {"status": "success"}
        result["checks"]["ssl"] = {"status": "success"}
        
        update_summary(result)
        
        summary = result["summary"]
        assert summary["successful_checks"] == 3
        assert summary["failed_checks"] == 0

    def test_update_summary_empty_checks(self):
        """Test summary with no checks"""
        result = new_domain_result("example.com")
        
        update_summary(result)
        
        summary = result["summary"]
        assert summary["total_checks"] == 0


class TestResultStructureValidation:
    """Test result structure validation"""

    def test_result_is_serializable(self):
        """Test that result can be JSON serialized"""
        import json
        
        result = new_domain_result("example.com")
        add_check_result(result, "whois", {"status": "success", "data": {"test": 123}})
        update_summary(result)
        
        # Should not raise
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

    def test_result_structure_consistency(self):
        """Test that result structure is consistent"""
        result = new_domain_result("example.com")
        
        # All top-level keys should be present
        expected_keys = {"domain", "timestamp", "status", "checks", "summary"}
        assert set(result.keys()) >= expected_keys


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_domain_name(self):
        """Test creating result with empty domain"""
        result = new_domain_result("")
        assert result["domain"] == ""

    def test_special_characters_in_domain(self):
        """Test domain names with special characters"""
        result = new_domain_result("xn--mgbaam7a8h.example")
        assert result["domain"] == "xn--mgbaam7a8h.example"

    def test_very_long_domain_name(self):
        """Test very long domain name"""
        long_domain = "a" * 200 + ".com"
        result = new_domain_result(long_domain)
        assert result["domain"] == long_domain

    def test_none_check_data(self):
        """Test adding None as check data"""
        result = new_domain_result("example.com")
        # Should handle gracefully
        add_check_result(result, "test", None)
        assert "test" in result["checks"]
