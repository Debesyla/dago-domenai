"""
Database query utility - v0.6
Provides CLI commands to query saved domain results.
"""

import sys
import os
import json
from src.utils.config import load_config, get_database_config
from src.utils.db import (
    get_domains, 
    get_domain_results, 
    get_latest_results,
    get_stats
)


def print_stats(db_url: str):
    """Print database statistics"""
    stats = get_stats(db_url)
    print("\n📊 Database Statistics:")
    print(f"  Total Domains: {stats.get('total_domains', 0)}")
    print(f"  Total Results: {stats.get('total_results', 0)}")
    print(f"  Last Check: {stats.get('last_check', 'Never')}")
    print(f"\n  Results by Status:")
    for status, count in stats.get('results_by_status', {}).items():
        print(f"    - {status}: {count}")


def print_domains(db_url: str, limit: int = 20):
    """Print all domains"""
    domains = get_domains(db_url, limit=limit)
    print(f"\n📋 Domains (showing {len(domains)}):")
    for i, domain in enumerate(domains, 1):
        print(f"  {i}. {domain['domain_name']}")
        print(f"     Created: {domain['created_at']}")
        print(f"     Last checked: {domain['updated_at']}")


def print_latest(db_url: str, limit: int = 10):
    """Print latest results"""
    results = get_latest_results(db_url, limit=limit)
    print(f"\n🕒 Latest Results (showing {len(results)}):")
    for result in results:
        domain = result['domain_name']
        status = result['status']
        checked = result['checked_at']
        
        # Get summary from data
        data = result['data']
        summary = data.get('summary', {})
        grade = summary.get('grade', 'N/A')
        https = '🔒' if summary.get('https') else '🔓'
        reachable = '✅' if summary.get('reachable') else '❌'
        
        print(f"  {domain}")
        print(f"    Status: {status} | Grade: {grade} {https} {reachable}")
        print(f"    Checked: {checked}")
        print()


def print_domain_details(db_url: str, domain: str):
    """Print detailed results for a specific domain"""
    results = get_domain_results(db_url, domain, limit=5)
    
    if not results:
        print(f"\n❌ No results found for domain: {domain}")
        return
    
    print(f"\n🔍 Results for: {domain}")
    print(f"   Total results: {len(results)}")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"  Result #{i} - {result['checked_at']}")
        print(f"  Status: {result['status']}")
        
        data = result['data']
        
        # Print meta
        meta = data.get('meta', {})
        print(f"  Execution time: {meta.get('execution_time_sec')}s")
        
        # Print summary
        summary = data.get('summary', {})
        print(f"  Grade: {summary.get('grade')}")
        print(f"  HTTPS: {summary.get('https')}")
        print(f"  Reachable: {summary.get('reachable')}")
        print(f"  Issues: {summary.get('issues')}")
        
        # Print checks
        checks = data.get('checks', {})
        print(f"  Checks:")
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                if 'error' in check_data:
                    print(f"    - {check_name}: ❌ {check_data['error']}")
                elif check_name == 'status':
                    print(f"    - {check_name}: {check_data.get('code')} ({check_data.get('duration_ms')}ms)")
                elif check_name == 'redirects':
                    print(f"    - {check_name}: {check_data.get('length')} redirects")
                elif check_name == 'ssl':
                    days = check_data.get('days_until_expiry')
                    issuer = check_data.get('issuer')
                    print(f"    - {check_name}: {issuer}, expires in {days} days")
                else:
                    print(f"    - {check_name}: ✅")
        print()


def main():
    """Main CLI interface"""
    config = load_config()
    db_config = get_database_config(config)
    db_url = os.environ.get('DATABASE_URL', db_config.get('postgres_url'))
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_db.py stats              - Show database statistics")
        print("  python query_db.py domains            - List all domains")
        print("  python query_db.py latest             - Show latest results")
        print("  python query_db.py domain <name>      - Show results for specific domain")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'stats':
        print_stats(db_url)
    elif command == 'domains':
        print_domains(db_url)
    elif command == 'latest':
        print_latest(db_url)
    elif command == 'domain':
        if len(sys.argv) < 3:
            print("Error: domain name required")
            print("Usage: python query_db.py domain <name>")
            sys.exit(1)
        domain_name = sys.argv[2]
        print_domain_details(db_url, domain_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
