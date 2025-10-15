"""
WHOIS Check Module (v0.8.1)

Checks if a domain is registered using domreg.lt DAS (Domain Availability Service).

DAS Protocol:
- Server: das.domreg.lt:4343
- Query format: "get 1.0 domain.lt\\n"
- Response: Domain name + Status
- Rate limit: "Several dozens of inquiries per second" (official documentation)

This implementation uses DAS instead of standard WHOIS (port 43) because:
- Port 43 has strict rate limits (100 queries per 30 minutes with IP blocking)
- DAS is designed for bulk checking and supports much higher throughput
- DAS is the official method recommended by domreg.lt for automated checks
"""

import socket
import asyncio
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DASClient:
    """
    Client for domreg.lt DAS (Domain Availability Service).
    
    DAS is the official protocol for bulk domain status checking from the
    Lithuanian domain registry. It supports "several dozens of inquiries per second"
    according to official documentation.
    
    Protocol Details:
    - Server: das.domreg.lt
    - Port: 4343 (TCP)
    - Query format: "get 1.0 domain.lt\\n"
    - Response format:
        % .lt registry DAS service
        Domain: domain.lt
        Status: available|registered|blocked|reserved|...
    """
    
    def __init__(self, server: str = 'das.domreg.lt', port: int = 4343, timeout: float = 5.0):
        """
        Initialize DAS client.
        
        Args:
            server: DAS server address (default: das.domreg.lt)
            port: DAS server port (default: 4343)
            timeout: Socket timeout in seconds (default: 5.0)
        """
        self.server = server
        self.port = port
        self.timeout = timeout
    
    async def check_domain(self, domain: str) -> Dict[str, any]:
        """
        Check domain registration status via DAS protocol.
        
        Args:
            domain: Domain name to check (e.g., "example.lt")
        
        Returns:
            {
                'registered': bool,  # True if registered, False if available, None on error
                'status': str,       # 'available', 'registered', 'blocked', etc.
                'domain': str,       # Domain name from response
                'raw_response': str  # Raw DAS response for debugging
            }
        """
        try:
            # Run blocking socket operation in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._query_das_socket, 
                domain
            )
            
            # Parse the DAS response
            parsed = self._parse_das_response(response, domain)
            
            return {
                'registered': parsed['status'] != 'available',
                'status': parsed['status'],
                'domain': parsed['domain'],
                'raw_response': response
            }
            
        except socket.timeout:
            logger.warning(f"DAS query timeout for domain: {domain}")
            return {
                'registered': None,
                'status': 'error',
                'domain': domain,
                'error': 'Connection timeout'
            }
        except socket.error as e:
            logger.error(f"DAS socket error for domain {domain}: {e}")
            return {
                'registered': None,
                'status': 'error',
                'domain': domain,
                'error': f'Socket error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"DAS query failed for domain {domain}: {e}")
            return {
                'registered': None,
                'status': 'error',
                'domain': domain,
                'error': str(e)
            }
    
    def _query_das_socket(self, domain: str) -> str:
        """
        Execute DAS query via TCP socket.
        
        This is a blocking operation and should be run in a thread pool executor.
        
        Args:
            domain: Domain name to query
        
        Returns:
            Raw DAS response text
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Connect to DAS server
            sock.connect((self.server, self.port))
            
            # Send DAS protocol query: "get 1.0 domain.lt\n"
            query = f"get 1.0 {domain}\n"
            sock.sendall(query.encode('utf-8'))
            
            # Read response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                
                # DAS responses are small, check if we have the complete response
                if b'\n' in response and b'Status:' in response:
                    break
            
            return response.decode('utf-8', errors='ignore')
            
        finally:
            sock.close()
    
    def _parse_das_response(self, response: str, query_domain: str) -> Dict[str, str]:
        """
        Parse DAS response to extract domain and status.
        
        Expected format:
            % .lt registry DAS service
            Domain: domain.lt
            Status: available
        
        Args:
            response: Raw DAS response
            query_domain: Original domain queried (fallback if parsing fails)
        
        Returns:
            {
                'domain': str,  # Domain name from response
                'status': str   # Status value (lowercase)
            }
        """
        domain = query_domain
        status = 'error'
        
        for line in response.split('\n'):
            line = line.strip()
            
            # Extract domain name
            if line.startswith('Domain:'):
                domain = line.split(':', 1)[1].strip()
            
            # Extract status
            elif line.startswith('Status:'):
                status = line.split(':', 1)[1].strip().lower()
        
        return {
            'domain': domain,
            'status': status
        }


class RateLimitedDAS:
    """
    Rate-limited wrapper for DAS queries.
    
    Implements token bucket-style rate limiting to ensure we don't exceed
    the configured queries per second. While DAS supports "several dozens per second",
    we default to a conservative 4 queries/second to be respectful of the registry.
    """
    
    def __init__(self, max_per_second: int = 4, server: str = 'das.domreg.lt', 
                 port: int = 4343, timeout: float = 5.0):
        """
        Initialize rate-limited DAS client.
        
        Args:
            max_per_second: Maximum queries per second (default: 4)
            server: DAS server address
            port: DAS server port
            timeout: Query timeout in seconds
        """
        self.client = DASClient(server=server, port=port, timeout=timeout)
        self.max_per_second = max_per_second
        self.semaphore = asyncio.Semaphore(max_per_second)
        self.min_interval = 1.0 / max_per_second
        self.last_query_time = None
        self.query_count = 0
        self.start_time = time.time()
    
    async def check_domain(self, domain: str) -> Dict[str, any]:
        """
        Check domain with rate limiting.
        
        Args:
            domain: Domain name to check
        
        Returns:
            Same as DASClient.check_domain()
        """
        async with self.semaphore:
            # Enforce minimum interval between queries
            if self.last_query_time:
                elapsed = time.time() - self.last_query_time
                if elapsed < self.min_interval:
                    sleep_time = self.min_interval - elapsed
                    await asyncio.sleep(sleep_time)
            
            self.last_query_time = time.time()
            self.query_count += 1
            
            result = await self.client.check_domain(domain)
            
            # Log rate limit stats periodically
            if self.query_count % 100 == 0:
                elapsed_total = time.time() - self.start_time
                actual_rate = self.query_count / elapsed_total if elapsed_total > 0 else 0
                logger.info(f"DAS rate stats: {self.query_count} queries, "
                          f"{actual_rate:.2f} queries/sec (limit: {self.max_per_second}/sec)")
            
            return result
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get rate limiting statistics.
        
        Returns:
            {
                'total_queries': int,
                'elapsed_time': float,
                'actual_rate': float,
                'configured_limit': int
            }
        """
        elapsed = time.time() - self.start_time
        return {
            'total_queries': self.query_count,
            'elapsed_time': elapsed,
            'actual_rate': self.query_count / elapsed if elapsed > 0 else 0,
            'configured_limit': self.max_per_second
        }


def check_domain_registration(domain: str) -> bool:
    """
    Synchronous wrapper to check if domain is registered.
    
    NOTE: This is a synchronous function for backward compatibility.
    Prefer using the async methods directly in async contexts.
    
    Args:
        domain: Domain name to check
    
    Returns:
        True if registered, False if available, None on error
    """
    async def _async_check():
        das = DASClient()
        result = await das.check_domain(domain)
        return result.get('registered')
    
    return asyncio.run(_async_check())


async def run_whois_check(domain: str, config: dict) -> dict:
    """
    Run WHOIS check using DAS protocol.
    
    This is the v0.8.1 implementation using domreg.lt official DAS service
    for bulk domain registration checking.
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary with optional 'whois' section:
                {
                    'whois': {
                        'server': 'das.domreg.lt',
                        'port': 4343,
                        'timeout': 5.0,
                        'rate_limit': 4
                    }
                }
    
    Returns:
        {
            'check': 'whois',
            'domain': str,
            'success': bool,          # True if check completed (even if unregistered)
            'registered': bool,       # True if domain is registered
            'status': str,            # DAS status: 'available', 'registered', 'blocked', etc.
            'error': str,             # Error message if check failed
            'meta': {
                'method': 'DAS',
                'server': str,
                'execution_time': float
            }
        }
    """
    start_time = time.time()
    
    # Get DAS configuration from config
    whois_config = config.get('whois', {})
    server = whois_config.get('server', 'das.domreg.lt')
    port = whois_config.get('port', 4343)
    timeout = whois_config.get('timeout', 5.0)
    
    try:
        # Create DAS client (no rate limiting here - orchestrator handles batch rate limiting)
        das = DASClient(server=server, port=port, timeout=timeout)
        result = await das.check_domain(domain)
        
        execution_time = time.time() - start_time
        
        # Determine if check was successful
        # Success = we got a definitive answer (registered or available)
        # Failure = error occurred (network issue, timeout, etc.)
        success = result.get('registered') is not None
        
        return {
            'check': 'whois',
            'domain': domain,
            'success': success,
            'registered': result.get('registered', True),  # Default to True on error (conservative)
            'status': result.get('status', 'unknown'),
            'error': result.get('error'),
            'meta': {
                'method': 'DAS',
                'server': f"{server}:{port}",
                'execution_time': execution_time
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"WHOIS check failed for {domain}: {e}")
        
        return {
            'check': 'whois',
            'domain': domain,
            'success': False,
            'registered': True,  # Conservative: assume registered on error to avoid false positives
            'status': 'error',
            'error': str(e),
            'meta': {
                'method': 'DAS',
                'server': f"{server}:{port}",
                'execution_time': execution_time
            }
        }


# Example usage and testing
if __name__ == "__main__":
    """
    Test DAS implementation with sample domains.
    
    Usage:
        python -m src.checks.whois_check
    """
    async def test_das():
        print("Testing DAS Protocol Implementation")
        print("=" * 60)
        
        # Test domains
        test_domains = [
            "google.lt",           # Should be registered
            "github.lt",           # Should be registered
            "nonexistent-xyz-test-12345.lt",  # Should be available
        ]
        
        das = DASClient()
        
        for domain in test_domains:
            print(f"\nChecking: {domain}")
            result = await das.check_domain(domain)
            
            print(f"  Registered: {result.get('registered')}")
            print(f"  Status: {result.get('status')}")
            if result.get('error'):
                print(f"  Error: {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("Testing rate-limited DAS")
        print("=" * 60)
        
        rate_limited = RateLimitedDAS(max_per_second=2)
        
        start = time.time()
        for domain in test_domains:
            result = await rate_limited.check_domain(domain)
            print(f"{domain}: {result.get('status')}")
        
        elapsed = time.time() - start
        stats = rate_limited.get_stats()
        
        print(f"\nRate limit stats:")
        print(f"  Total queries: {stats['total_queries']}")
        print(f"  Elapsed time: {stats['elapsed_time']:.2f}s")
        print(f"  Actual rate: {stats['actual_rate']:.2f} queries/sec")
        print(f"  Configured limit: {stats['configured_limit']} queries/sec")
    
    # Run the test
    asyncio.run(test_das())
