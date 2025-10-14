"""Test script for database functionality - v0.6"""
import os
from src.utils.config import load_config, get_database_config
from src.utils.db import (
    init_db, 
    get_domains, 
    get_domain_results, 
    get_latest_results,
    get_stats
)

def main():
    """Test database functions"""
    config = load_config()
    db_config = get_database_config(config)
    db_url = db_config.get('postgres_url')
    
    # Override with env if available
    db_url = os.environ.get('DATABASE_URL', db_url)
    
    print("="*60)
    print("DATABASE TEST - v0.6")
    print("="*60)
    print(f"Database URL: {db_url[:30]}...")
    print()
    
    # Test 1: Initialize database
    print("1. Testing database connection...")
    if init_db(db_url):
        print("   ✅ Database connection successful")
    else:
        print("   ❌ Database connection failed")
        return
    print()
    
    # Test 2: Get statistics
    print("2. Database statistics:")
    stats = get_stats(db_url)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Test 3: Get all domains
    print("3. Recent domains (limit 10):")
    domains = get_domains(db_url, limit=10)
    if domains:
        for domain in domains:
            print(f"   - {domain['domain_name']} (last checked: {domain['updated_at']})")
    else:
        print("   No domains found")
    print()
    
    # Test 4: Get latest results
    print("4. Latest results (limit 5):")
    results = get_latest_results(db_url, limit=5)
    if results:
        for result in results:
            print(f"   - {result['domain_name']} ({result['task_name']}): {result['status']} at {result['checked_at']}")
    else:
        print("   No results found")
    print()
    
    # Test 5: Get results for specific domain
    if domains:
        test_domain = domains[0]['domain_name']
        print(f"5. Results for {test_domain}:")
        domain_results = get_domain_results(db_url, test_domain, limit=3)
        for result in domain_results:
            print(f"   - {result['task_name']}: {result['status']} at {result['checked_at']}")
            # Show summary if available
            if 'summary' in result['data']:
                summary = result['data']['summary']
                print(f"     Grade: {summary.get('grade')}, HTTPS: {summary.get('https')}, Issues: {summary.get('issues')}")
    print()
    
    print("="*60)
    print("Database test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
