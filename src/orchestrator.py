"""Main orchestrator for domain analysis tasks"""
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

from src.utils.config import load_config, get_logging_config, get_database_config
from src.utils.logger import setup_logger
from src.core.schema import new_domain_result, update_result_meta, add_check_result, update_summary
from src.checks.status_check import run_status_check
from src.checks.redirect_check import run_redirect_check
from src.checks.robots_check import run_robots_check
from src.checks.sitemap_check import run_sitemap_check
from src.checks.ssl_check import run_ssl_check
from src.utils.db import save_result, init_db
from src.utils.export import ResultExporter


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
    checks_config = config.get('checks', {})
    
    # Run all enabled checks
    
    # 1. Status check
    if checks_config.get('status', {}).get('enabled', True):
        status_result = await run_status_check(domain, config)
        add_check_result(result, 'status', status_result)
        if 'error' in status_result:
            errors.append(f"status: {status_result['error']}")
    
    # 2. Redirect check
    if checks_config.get('redirect', {}).get('enabled', True):
        redirect_result = await run_redirect_check(domain, config)
        add_check_result(result, 'redirects', redirect_result)
        if 'error' in redirect_result:
            errors.append(f"redirects: {redirect_result['error']}")
    
    # 3. Robots.txt check
    if checks_config.get('robots', {}).get('enabled', True):
        robots_result = await run_robots_check(domain, config)
        add_check_result(result, 'robots', robots_result)
        if 'error' in robots_result:
            errors.append(f"robots: {robots_result['error']}")
    
    # 4. Sitemap check
    if checks_config.get('sitemap', {}).get('enabled', True):
        sitemap_result = await run_sitemap_check(domain, config)
        add_check_result(result, 'sitemap', sitemap_result)
        if 'error' in sitemap_result:
            errors.append(f"sitemap: {sitemap_result['error']}")
    
    # 5. SSL check
    if checks_config.get('ssl', {}).get('enabled', True):
        ssl_result = await run_ssl_check(domain, config)
        add_check_result(result, 'ssl', ssl_result)
        if 'error' in ssl_result:
            errors.append(f"ssl: {ssl_result['error']}")
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Determine overall status
    if errors:
        # If all checks failed, it's an error; otherwise partial success
        total_checks = sum(1 for check in checks_config.values() if isinstance(check, dict) and check.get('enabled', True))
        status = 'error' if len(errors) == total_checks else 'partial'
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
    
    # Get database configuration
    db_config = get_database_config(config)
    db_url = db_config.get('postgres_url')
    save_to_db = db_config.get('save_results', True)
    
    # Initialize database if saving is enabled
    if save_to_db and db_url:
        if not init_db(db_url):
            logger.warning("Database initialization failed, continuing without persistence")
            save_to_db = False
    
    logger.info(f"Processing {len(domains)} domains")
    
    results = []
    for domain in domains:
        result = await process_domain(domain, config, logger)
        results.append(result)
        
        # Save to database if enabled
        if save_to_db and db_url:
            task = result.get('meta', {}).get('task', 'basic-scan')
            if save_result(db_url, domain, task, result):
                logger.debug(f"Saved result for {domain} to database")
            else:
                logger.warning(f"Failed to save result for {domain}")
    
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
    
    # Initialize exporter with logger
    exporter = ResultExporter(export_dir="exports", logger=logger)
    
    # Log and export summary
    exporter.log_summary(results)
    
    # Export results to JSON (default)
    export_format = config.get('export', {}).get('format', 'json')
    export_enabled = config.get('export', {}).get('enabled', True)
    
    if export_enabled:
        try:
            if export_format == 'json' or export_format == 'both':
                json_path = exporter.export_json(results)
                logger.info(f"📄 Results exported to: {json_path}")
            
            if export_format == 'csv' or export_format == 'both':
                csv_path = exporter.export_csv(results)
                logger.info(f"📊 CSV exported to: {csv_path}")
            
            # Also export summary statistics
            summary_path = exporter.export_summary(results)
            logger.info(f"📈 Summary exported to: {summary_path}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
    
    logger.info(f"✅ Processing complete in {total_time:.2f}s")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
