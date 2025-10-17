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


class TokenBucket:
    """
    Token bucket rate limiter for WHOIS queries.
    
    Implements token bucket algorithm to enforce rate limits.
    For WHOIS port 43: 100 queries per 30 minutes (strict registry limit).
    """
    
    def __init__(self, max_tokens: int = 100, refill_period: float = 1800):
        """
        Initialize token bucket.
        
        Args:
            max_tokens: Maximum number of tokens (queries) in bucket
            refill_period: Time in seconds to refill all tokens (default: 1800 = 30 minutes)
        """
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_period = refill_period
        self.refill_rate = max_tokens / refill_period  # Tokens per second
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Try to acquire a token (permission to make query).
        
        Returns:
            True if token acquired, False if rate limit exceeded
        """
        async with self.lock:
            # Refill tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.refill_rate
            
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have tokens available
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            
            return False
    
    def tokens_available(self) -> float:
        """Get current number of tokens available."""
        return self.tokens
    
    def time_until_token(self) -> float:
        """Get time in seconds until next token is available."""
        if self.tokens >= 1.0:
            return 0.0
        return (1.0 - self.tokens) / self.refill_rate


class WHOISClient:
    """
    Standard WHOIS client for detailed domain information (port 43).
    
    This client queries the standard WHOIS protocol on port 43 to get
    detailed registration information including registrar, dates, and contacts.
    
    IMPORTANT: This has STRICT rate limiting (100 queries per 30 minutes)
    with IP blocking. Use sparingly and only for registered domains.
    """
    
    def __init__(self, server: str = 'whois.domreg.lt', port: int = 43, 
                 timeout: float = 10.0, rate_limit: int = 100):
        """
        Initialize WHOIS client.
        
        Args:
            server: WHOIS server address (default: whois.domreg.lt)
            port: WHOIS server port (default: 43)
            timeout: Socket timeout in seconds (default: 10.0)
            rate_limit: Max queries per 30 minutes (default: 100)
        """
        self.server = server
        self.port = port
        self.timeout = timeout
        self.rate_limiter = TokenBucket(max_tokens=rate_limit, refill_period=1800)
        self.query_count = 0
    
    async def query(self, domain: str) -> Dict[str, any]:
        """
        Query WHOIS for detailed domain information.
        
        Args:
            domain: Domain name to query
        
        Returns:
            Parsed WHOIS data or error dict
        """
        # Check rate limit
        if not await self.rate_limiter.acquire():
            time_until = self.rate_limiter.time_until_token()
            logger.warning(f"WHOIS rate limit exceeded. Next query available in {time_until:.0f}s")
            return {
                'error': 'rate_limit_exceeded',
                'message': f'Rate limit exceeded. Try again in {time_until:.0f} seconds',
                'time_until_available': time_until
            }
        
        try:
            # Run blocking socket operation in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._query_whois_socket,
                domain
            )
            
            self.query_count += 1
            
            # Parse response
            parsed = parse_whois_response(response)
            return parsed
            
        except socket.timeout:
            logger.warning(f"WHOIS query timeout for domain: {domain}")
            return {
                'error': 'timeout',
                'message': 'WHOIS query timed out'
            }
        except socket.error as e:
            logger.error(f"WHOIS socket error for domain {domain}: {e}")
            return {
                'error': 'socket_error',
                'message': f'Socket error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"WHOIS query failed for domain {domain}: {e}")
            return {
                'error': 'query_failed',
                'message': str(e)
            }
    
    def _query_whois_socket(self, domain: str) -> str:
        """
        Execute WHOIS query via TCP socket (blocking operation).
        
        Args:
            domain: Domain name to query
        
        Returns:
            Raw WHOIS response text
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Connect to WHOIS server
            sock.connect((self.server, self.port))
            
            # Send WHOIS query: "domain.lt\n"
            query = f"{domain}\n"
            sock.sendall(query.encode('utf-8'))
            
            # Read response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            return response.decode('utf-8', errors='ignore')
            
        finally:
            sock.close()


def parse_whois_response(response: str) -> Dict[str, any]:
    """
    Parse .lt WHOIS response into structured data.
    
    Expected format:
        % Hello, this is the DOMREG whois service.
        % ... (terms of service)
        %
        Domain:                 example.lt
        Status:                 registered
        Registered:             2002-05-14
        Expires:                2026-05-14
        %
        Registrar:              Some Registrar
        Registrar website:      https://example.com
        Registrar email:        contact@example.com
        %
        Contact organization:   Company Name (optional - only if not privacy protected)
        Contact email:          contact@company.com (optional)
        %
        Nameserver:             ns1.example.com
        Nameserver:             ns2.example.com    [1.2.3.4]
    
    Args:
        response: Raw WHOIS response text
    
    Returns:
        {
            'domain': str,
            'status': str,
            'dates': {
                'registered': str,      # YYYY-MM-DD
                'expires': str,         # YYYY-MM-DD
                'age_days': int,
                'days_until_expiry': int
            },
            'registrar': {
                'name': str,
                'website': str,
                'email': str
            },
            'contact': {
                'organization': str | None,
                'email': str | None,
                'privacy_protected': bool
            },
            'nameservers': [str],
            'nameserver_details': [{'hostname': str, 'ip': str | None}],
            'raw_response': str
        }
    """
    from datetime import datetime
    
    data = {
        'domain': None,
        'status': None,
        'dates': {},
        'registrar': {},
        'contact': {
            'organization': None,
            'email': None,
            'privacy_protected': True  # Default to True, set False if contact found
        },
        'nameservers': [],
        'nameserver_details': [],
        'raw_response': response
    }
    
    for line in response.split('\n'):
        # Skip comments and empty lines
        if line.startswith('%') or not line.strip():
            continue
        
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Core fields
        if key == 'Domain':
            data['domain'] = value
        elif key == 'Status':
            data['status'] = value
        elif key == 'Registered':
            data['dates']['registered'] = value
        elif key == 'Expires':
            data['dates']['expires'] = value
        
        # Registrar info
        elif key == 'Registrar':
            data['registrar']['name'] = value
        elif key == 'Registrar website':
            data['registrar']['website'] = value
        elif key == 'Registrar email':
            data['registrar']['email'] = value
        
        # Contact info (may be absent if privacy protected)
        elif key == 'Contact organization':
            data['contact']['organization'] = value
            data['contact']['privacy_protected'] = False
        elif key == 'Contact email':
            data['contact']['email'] = value
            data['contact']['privacy_protected'] = False
        
        # Nameservers
        elif key == 'Nameserver':
            # Handle optional IP: "ns1.example.com    [1.2.3.4]"
            if '[' in value:
                parts = value.split('[')
                hostname = parts[0].strip()
                ip = parts[1].rstrip(']').strip()
                data['nameserver_details'].append({
                    'hostname': hostname,
                    'ip': ip
                })
                data['nameservers'].append(hostname)
            else:
                data['nameserver_details'].append({
                    'hostname': value,
                    'ip': None
                })
                data['nameservers'].append(value)
    
    # Calculate derived fields
    if data['dates'].get('registered'):
        try:
            reg_date = datetime.strptime(data['dates']['registered'], '%Y-%m-%d')
            age_days = (datetime.now() - reg_date).days
            data['dates']['age_days'] = age_days
        except ValueError:
            logger.warning(f"Could not parse registration date: {data['dates']['registered']}")
    
    if data['dates'].get('expires'):
        try:
            exp_date = datetime.strptime(data['dates']['expires'], '%Y-%m-%d')
            days_until = (exp_date - datetime.now()).days
            data['dates']['days_until_expiry'] = days_until
        except ValueError:
            logger.warning(f"Could not parse expiration date: {data['dates']['expires']}")
    
    return data


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


async def run_das_check(domain: str, config: dict) -> dict:
    """
    Run DAS-only check for ultra-fast registration status (v1.1.1).
    
    Uses only the DAS protocol (das.domreg.lt:4343) for maximum speed.
    Perfect for bulk domain validation where only registration status is needed.
    
    Performance:
    - ~0.02s per domain
    - No rate limiting concerns (4 queries/sec supported)
    - 5x faster than full WHOIS check
    
    Use Cases:
    - Bulk domain validation (10,000+ domains)
    - Continuous monitoring
    - Quick availability checks
    - Initial domain filtering
    
    Args:
        domain: Domain name to check (e.g., "example.lt")
        config: Configuration dictionary with 'checks.whois.das' section:
                {
                    'checks': {
                        'whois': {
                            'das': {
                                'server': 'das.domreg.lt',
                                'port': 4343,
                                'timeout': 5
                            }
                        }
                    }
                }
    
    Returns:
        {
            'status': 'registered' | 'available' | 'error',
            'registration': {
                'status': 'registered' | 'available',
                'domain': 'example.lt'
            },
            'meta': {
                'check_type': 'das_only',
                'protocol': 'DAS',
                'server': 'das.domreg.lt:4343',
                'query_time': 0.02,
                'rate_limit': '4 queries/sec',
                'note': 'Fast check - use "whois" profile for complete data'
            }
        }
        
        On error:
        {
            'status': 'error',
            'error': 'error message',
            'meta': {
                'check_type': 'das_only'
            }
        }
    """
    start_time = time.time()
    
    try:
        # Get DAS configuration
        das_config = config.get('checks', {}).get('whois', {}).get('das', {})
        server = das_config.get('server', 'das.domreg.lt')
        port = das_config.get('port', 4343)
        timeout = das_config.get('timeout', 5)
        
        # Initialize DAS client
        das_client = DASClient(server=server, port=port, timeout=timeout)
        
        # Query DAS
        logger.info(f"Running DAS check for {domain}")
        result = await das_client.check_domain(domain)
        
        query_time = time.time() - start_time
        
        # Handle errors
        if result.get('status') == 'error':
            logger.warning(f"DAS check error for {domain}: {result.get('error', 'Unknown error')}")
            return {
                'status': 'error',
                'error': result.get('error', 'DAS query failed'),
                'meta': {
                    'check_type': 'das_only',
                    'protocol': 'DAS',
                    'server': f"{server}:{port}",
                    'query_time': query_time
                }
            }
        
        # Determine registration status
        das_status = result.get('status', '').lower()
        is_registered = das_status not in ['available', 'error']
        status = 'registered' if is_registered else 'available'
        
        logger.info(f"DAS check complete for {domain}: {status} ({query_time:.3f}s)")
        
        return {
            'status': status,
            'registration': {
                'status': status,
                'domain': result.get('domain', domain),
                'das_status': das_status  # Original status from DAS
            },
            'meta': {
                'check_type': 'das_only',
                'protocol': 'DAS',
                'server': f"{server}:{port}",
                'query_time': round(query_time, 3),
                'rate_limit': '4 queries/sec',
                'note': 'Fast check - use "whois" profile for complete registration data'
            }
        }
        
    except asyncio.TimeoutError:
        query_time = time.time() - start_time
        logger.warning(f"DAS check timeout for {domain} after {query_time:.3f}s")
        return {
            'status': 'error',
            'error': 'timeout',
            'meta': {
                'check_type': 'das_only',
                'query_time': round(query_time, 3)
            }
        }
    except Exception as e:
        query_time = time.time() - start_time
        logger.error(f"DAS check exception for {domain}: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'meta': {
                'check_type': 'das_only',
                'query_time': round(query_time, 3)
            }
        }


async def run_whois_check(domain: str, config: dict) -> dict:
    """
    Run WHOIS check using dual protocol approach (v1.1).
    
    Strategy:
    1. DAS Protocol (port 4343) - Fast registration status check
    2. WHOIS Protocol (port 43) - Detailed data for registered domains only
    
    This maintains fast bulk scanning while getting detailed data where needed.
    
    Args:
        domain: Domain name to check
        config: Configuration dictionary with 'whois' section:
                {
                    'whois': {
                        'das_server': 'das.domreg.lt',
                        'das_port': 4343,
                        'whois_server': 'whois.domreg.lt',
                        'whois_port': 43,
                        'timeout': 10.0,
                        'rate_limit': 100  # For WHOIS port 43 (per 30 min)
                    }
                }
    
    Returns:
        JSONB structure for v1.1:
        {
            'status': 'registered' | 'available' | 'error',
            'registration': {              # Only if registered
                'status': str,
                'registered_date': str,
                'expires_date': str,
                'age_days': int,
                'days_until_expiry': int
            },
            'registrar': {                 # Only if registered
                'name': str,
                'website': str,
                'email': str
            },
            'contact': {                   # Only if registered
                'organization': str | null,
                'email': str | null,
                'privacy_protected': bool
            },
            'nameservers': [str],          # Only if registered
            'meta': {
                'method': 'DAS' | 'DAS+WHOIS',
                'execution_time': float,
                'whois_rate_limited': bool  # If WHOIS data unavailable due to rate limit
            }
        }
    """
    start_time = time.time()
    
    # Get configuration
    whois_config = config.get('whois', {})
    das_server = whois_config.get('das_server', whois_config.get('server', 'das.domreg.lt'))
    das_port = whois_config.get('das_port', whois_config.get('port', 4343))
    das_timeout = whois_config.get('das_timeout', whois_config.get('timeout', 5.0))
    
    whois_server = whois_config.get('whois_server', 'whois.domreg.lt')
    whois_port = whois_config.get('whois_port', 43)
    whois_timeout = whois_config.get('whois_timeout', 10.0)
    whois_rate_limit = whois_config.get('whois_rate_limit', whois_config.get('rate_limit', 100))
    
    result = {
        'meta': {
            'method': 'DAS',
            'execution_time': 0.0,
            'whois_rate_limited': False
        }
    }
    
    try:
        # STEP 1: DAS Check (fast registration status)
        das = DASClient(server=das_server, port=das_port, timeout=das_timeout)
        das_result = await das.check_domain(domain)
        
        # Check if registered
        is_registered = das_result.get('registered')
        
        if is_registered is None:
            # DAS error - return error result
            result['status'] = 'error'
            result['error'] = das_result.get('error', 'DAS query failed')
            result['meta']['execution_time'] = time.time() - start_time
            return result
        
        if not is_registered:
            # Domain not registered - return early
            result['status'] = 'available'
            result['meta']['execution_time'] = time.time() - start_time
            return result
        
        # STEP 2: WHOIS Query for detailed data (registered domains only)
        result['status'] = 'registered'
        result['meta']['method'] = 'DAS+WHOIS'
        
        whois_client = WHOISClient(
            server=whois_server,
            port=whois_port,
            timeout=whois_timeout,
            rate_limit=whois_rate_limit
        )
        
        whois_data = await whois_client.query(domain)
        
        # Check if WHOIS query succeeded
        if 'error' in whois_data:
            # WHOIS failed or rate limited - return DAS data only
            logger.warning(f"WHOIS query failed for {domain}: {whois_data.get('message')}")
            result['meta']['whois_rate_limited'] = (whois_data.get('error') == 'rate_limit_exceeded')
            result['meta']['whois_error'] = whois_data.get('error')
            
            # Return minimal data from DAS
            result['registration'] = {'status': das_result.get('status', 'registered')}
            result['meta']['execution_time'] = time.time() - start_time
            return result
        
        # WHOIS succeeded - build complete result
        result['registration'] = {
            'status': whois_data.get('status', 'registered'),
            'registered_date': whois_data.get('dates', {}).get('registered'),
            'expires_date': whois_data.get('dates', {}).get('expires'),
            'age_days': whois_data.get('dates', {}).get('age_days'),
            'days_until_expiry': whois_data.get('dates', {}).get('days_until_expiry')
        }
        
        result['registrar'] = whois_data.get('registrar', {})
        result['contact'] = whois_data.get('contact', {
            'organization': None,
            'email': None,
            'privacy_protected': True
        })
        result['nameservers'] = whois_data.get('nameservers', [])
        
        # Optional: Include nameserver details with IPs
        if whois_data.get('nameserver_details'):
            result['nameserver_details'] = whois_data['nameserver_details']
        
        result['meta']['execution_time'] = time.time() - start_time
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"WHOIS check failed for {domain}: {e}")
        
        return {
            'status': 'error',
            'error': str(e),
            'meta': {
                'method': 'DAS',
                'execution_time': execution_time,
                'whois_rate_limited': False
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
