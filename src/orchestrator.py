"""Main orchestrator for domain analysis tasks"""
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

from src.utils.config import load_config, get_logging_config
from src.utils.logger import setup_logger
from src.core.schema import new_domain_result, update_result_meta, add_check_result, update_summary
from src.checks.status_check import run_status_check


async def process_domain(domain: str, config: dict, logger) -> dict:
    """
    Process a single domain and return the result JSON.
    
    Args:
        domain: The domain to analyze
        config: Configuration dictionary
        logger: Logger instance
        
    Returns:
        Standard JSON result object
    """
    import time
    start_time = time.time()
    
    task = config.get('orchestrator', {}).get('default_task', 'basic-scan')
    logger.info(f"Starting analysis for: {domain}")
    
    # Initialize result object
    result = new_domain_result(domain, task)
    
    errors = []
    
    # Run status check
    status_result = await run_status_check(domain, config)
    add_check_result(result, 'status', status_result)
    
    # Check if status check had errors
    if 'error' in status_result:
        errors.append(f"status: {status_result['error']}")
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Determine overall status
    if errors:
        status = 'error' if len(errors) == 1 else 'partial'
    else:
        status = 'success'
    
    # Update metadata and summary
    update_result_meta(result, execution_time, status, errors if errors else None)
    update_summary(result)
    
    logger.info(f"Completed analysis for: {domain}")
    return result


async def process_domains(domains: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process multiple domains sequentially.
    
    Args:
        domains: List of domain names
        config: Full configuration dict
        
    Returns:
        List of domain results
    """
    log_config = get_logging_config(config)
    logger = setup_logger(**log_config)
    
    logger.info(f"Processing {len(domains)} domains")
    
    results = []
    for domain in domains:
        result = await process_domain(domain, config, logger)
        results.append(result)
    
    return results


def load_domains_from_file(filepath: str) -> List[str]:
    """
    Load domains from a text file (one per line).
    
    Args:
        filepath: Path to domains file
        
    Returns:
        List of domain names
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Domains file not found: {filepath}")
    
    with open(path, 'r') as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    return domains


async def main():
    """Main entry point for orchestrator"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m src.orchestrator <domains_file>")
        print("   or: python -m src.orchestrator --domain <domain>")
        print("\nExample: python -m src.orchestrator domains.txt")
        sys.exit(1)
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    log_config = get_logging_config(config)
    logger = setup_logger(**log_config)
    
    # Get domains
    try:
        if sys.argv[1] == '--domain':
            if len(sys.argv) < 3:
                print("Error: --domain requires a domain name")
                sys.exit(1)
            domains = [sys.argv[2]]
        else:
            domains_file = sys.argv[1]
            domains = load_domains_from_file(domains_file)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading domains: {e}")
        sys.exit(1)
    
    if not domains:
        logger.error("No domains to process")
        sys.exit(1)
    
    logger.info(f"Loaded {len(domains)} domain(s)")
    
    # Process domains
    start_time = time.time()
    results = await process_domains(domains, config)
    total_time = time.time() - start_time
    
    # Log summary
    success_count = sum(1 for r in results if r['meta']['status'] == 'success')
    error_count = len(results) - success_count
    
    logger.info(f"Processing complete in {total_time:.2f}s")
    logger.info(f"Success: {success_count}, Errors: {error_count}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
