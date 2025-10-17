"""Main orchestrator for domain analysis tasks

v0.10 - Composable Profile System:
  - Support for profile-based execution (--profiles dns,ssl,seo)
  - Automatic dependency resolution
  - Backward compatible with legacy check flags
  - Early bailout optimization maintained
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.utils.config import load_config, get_logging_config, get_database_config
from src.utils.logger import setup_logger
from src.core.schema import new_domain_result, update_result_meta, add_check_result, update_summary
from src.checks.status_check import run_status_check
from src.checks.redirect_check import run_redirect_check
from src.checks.robots_check import run_robots_check
from src.checks.sitemap_check import run_sitemap_check
from src.checks.ssl_check import run_ssl_check
from src.checks.whois_check import run_whois_check, run_das_check, check_domain_registration
from src.checks.active_check import run_active_check, check_domain_active
from src.utils.db import save_result, init_db, update_domain_flags
from src.utils.export import ResultExporter

# v0.10 - Profile system imports
try:
    from src.profiles.profile_loader import (
        resolve_profile_dependencies,
        get_profile_execution_plan,
        parse_profile_string,
        validate_profile_combination,
    )
    PROFILES_AVAILABLE = True
except ImportError:
    PROFILES_AVAILABLE = False


def determine_checks_to_run(config: dict, profiles: Optional[List[str]] = None, logger=None) -> Dict[str, bool]:
    """
    Determine which checks to run based on profiles or legacy config.
    
    v0.10 - Profile-aware check selection:
    - If profiles specified: Use profile system to determine checks
    - If no profiles: Fall back to legacy checks config
    
    Args:
        config: Configuration dictionary
        profiles: List of profile names (None = use legacy)
        logger: Optional logger for debug messages
        
    Returns:
        Dict mapping check names to enabled status
        Example: {'whois': True, 'dns': False, 'http': True, ...}
    """
    # Legacy mode: Use checks config directly
    if not profiles or not PROFILES_AVAILABLE:
        checks_config = config.get('checks', {})
        return {
            'whois': checks_config.get('whois', {}).get('enabled', True),
            'status': checks_config.get('status', {}).get('enabled', True),
            'redirect': checks_config.get('redirect', {}).get('enabled', True),
            'robots': checks_config.get('robots', {}).get('enabled', True),
            'sitemap': checks_config.get('sitemap', {}).get('enabled', True),
            'ssl': checks_config.get('ssl', {}).get('enabled', True),
        }
    
    # Profile mode: Resolve profiles and determine checks
    try:
        execution_order = resolve_profile_dependencies(profiles)
        if logger:
            logger.info(f"📋 Profile execution order: {' → '.join(execution_order)}")
        
        # Build checks dict based on profiles
        checks = {
            'quick-whois': 'quick-whois' in execution_order,
            'whois': 'whois' in execution_order,
            'http': 'http' in execution_order,
            'ssl': 'ssl' in execution_order,
            'dns': 'dns' in execution_order,
            'status': 'http' in execution_order,  # status/redirect are part of http profile
            'redirect': 'http' in execution_order,
            'robots': 'seo' in execution_order,  # robots/sitemap are part of seo profile
            'sitemap': 'seo' in execution_order,
        }
        
        return checks
    except Exception as e:
        if logger:
            logger.warning(f"Profile resolution failed: {e}, falling back to legacy mode")
        return determine_checks_to_run(config, profiles=None, logger=logger)


async def process_domain(domain: str, config: dict, logger, profiles: Optional[List[str]] = None) -> dict:
    """
    Process a single domain with early bailout optimization.
    
    v0.8 Logic:
    1. Run WHOIS check first
    2. If NOT registered → skip all other checks, save result
    3. If registered → run active check (status + redirect)
    4. If NOT active → skip remaining checks, save result
    5. If active → run full check suite
    
    v0.10 Enhancement:
    - Accepts optional profiles parameter for profile-based execution
    - Resolves profile dependencies automatically
    - Maintains backward compatibility with legacy check flags
    - Adds profile metadata to results
    
    Args:
        domain: The domain to analyze
        config: Configuration dictionary
        logger: Logger instance
        profiles: Optional list of profile names (e.g., ['dns', 'ssl'])
        
    Returns:
        Standard JSON result object with profile metadata
    """
    import time
    start_time = time.time()
    
    # Determine task name based on profiles or legacy config
    if profiles:
        task = f"profiles:{','.join(profiles)}"
    else:
        task = config.get('orchestrator', {}).get('default_task', 'basic-scan')
    
    logger.info(f"Starting analysis for: {domain}")
    
    # Determine which checks to run
    checks_to_run = determine_checks_to_run(config, profiles, logger)
    
    # Initialize result object
    result = new_domain_result(domain, task)
    
    # Add profile metadata if using profiles
    if profiles and PROFILES_AVAILABLE:
        try:
            plan = get_profile_execution_plan(profiles)
            result['meta']['profiles'] = {
                'requested': profiles,
                'execution_order': plan['execution_order'],
                'estimated_duration': plan['estimated_duration'],
            }
            logger.debug(f"Profile plan: {plan['execution_order']}")
        except Exception as e:
            logger.warning(f"Failed to generate execution plan: {e}")
    
    errors = []
    checks_config = config.get('checks', {})
    db_config = get_database_config(config)
    
    # STEP 1: WHOIS Check (determines if domain is registered)
    # Support both quick-whois (DAS only) and whois (full)
    is_registered = True  # Default assumption
    
    if checks_to_run.get('quick-whois', False):
        # Quick WHOIS check (DAS only) - ultra-fast
        quick_whois_result = await run_das_check(domain, config)
        add_check_result(result, 'quick-whois', quick_whois_result)
        
        # Determine registration status from DAS check
        if quick_whois_result.get('status') != 'error':
            is_registered = quick_whois_result.get('status') == 'registered'
        
        # Update database with registration status
        if db_config.get('save_results', True):
            update_domain_flags(db_config['postgres_url'], domain, is_registered=is_registered)
        
        # EARLY BAILOUT: If not registered, skip all other checks
        if not is_registered:
            logger.info(f"⏭️  Domain {domain} is NOT registered - skipping all checks")
            execution_time = time.time() - start_time
            update_result_meta(result, execution_time, 'skipped', errors)
            result['meta']['skip_reason'] = 'unregistered'
            logger.info(f"Completed analysis for: {domain} (skipped - unregistered)")
            return result
            
    elif checks_to_run.get('whois', True):
        # Full WHOIS check (DAS + WHOIS port 43) - complete data
        whois_result = await run_whois_check(domain, config)
        add_check_result(result, 'whois', whois_result)
        is_registered = whois_result.get('registered', True)
        
        # Update database with registration status
        if db_config.get('save_results', True):
            update_domain_flags(db_config['postgres_url'], domain, is_registered=is_registered)
        
        # EARLY BAILOUT: If not registered, skip all other checks
        if not is_registered:
            logger.info(f"⏭️  Domain {domain} is NOT registered - skipping all checks")
            execution_time = time.time() - start_time
            update_result_meta(result, execution_time, 'skipped', errors)
            result['meta']['skip_reason'] = 'unregistered'
            logger.info(f"Completed analysis for: {domain} (skipped - unregistered)")
            return result
    
    # STEP 2: Run Status and Redirect checks to determine if active
    status_result = None
    redirect_result = None
    
    if checks_to_run.get('status', True):
        status_result = await run_status_check(domain, config)
        add_check_result(result, 'status', status_result)
        if 'error' in status_result:
            errors.append(f"status: {status_result['error']}")
    
    if checks_to_run.get('redirect', True):
        redirect_result = await run_redirect_check(domain, config)
        add_check_result(result, 'redirects', redirect_result)
        if 'error' in redirect_result:
            errors.append(f"redirects: {redirect_result['error']}")
    
    # STEP 3: Determine if domain is active
    active_result = await run_active_check(domain, config, status_result, redirect_result)
    add_check_result(result, 'active', active_result)
    is_active = active_result.get('active', True)
    
    # Process captured .lt domains from redirect chain
    captured_domains = active_result.get('captured_domains', [])
    if captured_domains and db_config.get('save_results', True):
        try:
            from src.checks.active_check import insert_captured_domains
            inserted_count = insert_captured_domains(
                db_config['postgres_url'], 
                captured_domains, 
                domain
            )
            if inserted_count > 0:
                logger.info(f"📥 Added {inserted_count} new .lt domain(s) for future checking")
        except Exception as e:
            logger.warning(f"Failed to insert captured domains: {e}")
    
    # Update database with active status
    if db_config.get('save_results', True):
        update_domain_flags(db_config['postgres_url'], domain, is_active=is_active)
    
    # EARLY BAILOUT: If not active, skip remaining expensive checks
    if not is_active:
        logger.info(f"⏭️  Domain {domain} is NOT active - skipping remaining checks")
        logger.info(f"   Reason: {active_result.get('reason', 'Unknown')}")
        execution_time = time.time() - start_time
        update_result_meta(result, execution_time, 'partial', errors)
        result['meta']['skip_reason'] = 'inactive'
        logger.info(f"Completed analysis for: {domain} (partial - inactive)")
        return result
    
    # STEP 4: Run full check suite for active domains
    logger.info(f"✅ Domain {domain} is ACTIVE - running full checks")
    
    # 3. Robots.txt check
    if checks_to_run.get('robots', True):
        robots_result = await run_robots_check(domain, config)
        add_check_result(result, 'robots', robots_result)
        if 'error' in robots_result:
            errors.append(f"robots: {robots_result['error']}")
    
    # 4. Sitemap check
    if checks_to_run.get('sitemap', True):
        sitemap_result = await run_sitemap_check(domain, config)
        add_check_result(result, 'sitemap', sitemap_result)
        if 'error' in sitemap_result:
            errors.append(f"sitemap: {sitemap_result['error']}")
    
    # 5. SSL check
    if checks_to_run.get('ssl', True):
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


async def process_domains(domains: List[str], config: Dict[str, Any], profiles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Process multiple domains sequentially.
    
    v0.10 - Profile support:
    - Accepts optional profiles parameter
    - Passes profiles to each domain processing
    
    Args:
        domains: List of domain names
        config: Full configuration dict
        profiles: Optional list of profile names
        
    Returns:
        List of domain results
    """
    log_config = get_logging_config(config)
    logger = setup_logger(**log_config)
    
    # Log profile information if using profiles
    if profiles and PROFILES_AVAILABLE:
        logger.info(f"🎯 Using profiles: {', '.join(profiles)}")
        try:
            plan = get_profile_execution_plan(profiles)
            logger.info(f"📊 Execution plan: {len(plan['execution_order'])} profiles, ~{plan['estimated_duration']}")
        except Exception as e:
            logger.warning(f"Could not generate execution plan: {e}")
    
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
        result = await process_domain(domain, config, logger, profiles)
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
        print("Usage: python3 -m src.orchestrator <domains_file> [--profiles PROFILES]")
        print("   or: python3 -m src.orchestrator --domain <domain> [--profiles PROFILES]")
        print("\nProfiles (v0.10):")
        print("  --profiles dns,ssl,seo    : Run specific profiles")
        print("  --profiles quick-check    : Fast filtering")
        print("  --profiles standard       : General analysis (default)")
        print("  --profiles complete       : Comprehensive analysis")
        print("\nExamples:")
        print("  python3 -m src.orchestrator domains.txt")
        print("  python3 -m src.orchestrator domains.txt --profiles dns,ssl")
        print("  python3 -m src.orchestrator --domain example.lt --profiles quick-check")
        sys.exit(1)
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    log_config = get_logging_config(config)
    logger = setup_logger(**log_config)
    
    # Parse profiles argument
    profiles = None
    args = sys.argv[1:]
    
    if '--profiles' in args:
        profiles_idx = args.index('--profiles')
        if profiles_idx + 1 >= len(args):
            logger.error("--profiles requires a profile list")
            sys.exit(1)
        
        profile_str = args[profiles_idx + 1]
        profiles = parse_profile_string(profile_str)
        
        # Validate profiles
        if PROFILES_AVAILABLE:
            is_valid, error = validate_profile_combination(profiles)
            if not is_valid:
                logger.error(f"Invalid profile combination: {error}")
                sys.exit(1)
        else:
            logger.warning("Profile system not available, ignoring --profiles")
            profiles = None
        
        # Remove --profiles and its value from args
        args = args[:profiles_idx] + args[profiles_idx+2:]
    
    # Get domains
    try:
        if '--domain' in args:
            domain_idx = args.index('--domain')
            if domain_idx + 1 >= len(args):
                logger.error("--domain requires a domain name")
                sys.exit(1)
            domains = [args[domain_idx + 1]]
        elif len(args) > 0:
            domains_file = args[0]
            domains = load_domains_from_file(domains_file)
        else:
            logger.error("No domains specified")
            sys.exit(1)
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
    results = await process_domains(domains, config, profiles)
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
