"""JSON result schema factory for domain checks"""
from datetime import datetime, timezone
from typing import Dict, List, Any


def new_domain_result(domain: str, task: str = "basic_scan") -> Dict[str, Any]:
    """
    Create a new domain result structure following the standard schema.
    
    Args:
        domain: Domain name (e.g., "example.com")
        task: Task name (e.g., "basic_scan", "full_scan")
        
    Returns:
        Dict with meta, checks, and summary sections
    """
    return {
        "domain": domain,
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "execution_time_sec": 0.0,
            "status": "pending",
            "errors": [],
            "schema_version": "1.0"
        },
        "checks": {},
        "summary": {
            "reachable": False,
            "https": False,
            "issues": 0,
            "warnings": 0,
            "grade": "N/A"
        }
    }


def update_result_meta(
    result: Dict[str, Any],
    execution_time: float,
    status: str,
    errors: List[str] = None
) -> None:
    """
    Update the meta section of a result.
    
    Args:
        result: The domain result dict
        execution_time: Total execution time in seconds
        status: Overall status ("success", "partial", "error")
        errors: List of error messages
    """
    result["meta"]["execution_time_sec"] = round(execution_time, 2)
    result["meta"]["status"] = status
    if errors:
        result["meta"]["errors"] = errors


def add_check_result(
    result: Dict[str, Any],
    check_name: str,
    check_data: Dict[str, Any]
) -> None:
    """
    Add a check result to the checks section.
    
    Args:
        result: The domain result dict
        check_name: Name of the check (e.g., "status", "ssl")
        check_data: Check-specific data dict
    """
    result["checks"][check_name] = check_data


def update_summary(result: Dict[str, Any]) -> None:
    """
    Update the summary section based on check results.
    
    Args:
        result: The domain result dict
    """
    checks = result.get("checks", {})
    
    # Determine reachability from status check
    if "status" in checks:
        status_check = checks["status"]
        result["summary"]["reachable"] = status_check.get("ok", False)
        final_url = status_check.get("final_url")
        result["summary"]["https"] = final_url.startswith("https://") if final_url else False
    
    # Count issues and warnings
    issues = 0
    warnings = 0
    
    for check_name, check_data in checks.items():
        if check_data.get("error"):
            issues += 1
        # Add more logic here for warnings based on check-specific criteria
    
    result["summary"]["issues"] = issues
    result["summary"]["warnings"] = warnings
    
    # Simple grading logic
    if not result["summary"]["reachable"]:
        result["summary"]["grade"] = "F"
    elif issues > 2:
        result["summary"]["grade"] = "D"
    elif issues > 0:
        result["summary"]["grade"] = "C"
    elif warnings > 0:
        result["summary"]["grade"] = "B"
    else:
        result["summary"]["grade"] = "A"
