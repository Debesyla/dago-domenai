"""
SSL Certificate Check - v0.5
Checks SSL certificate validity, issuer, and expiration.
"""

import ssl
import socket
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from src.utils.logger import safe_run_async


@safe_run_async
async def run_ssl_check(domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check SSL certificate details.
    
    Args:
        domain: The domain to check (without protocol)
        config: Configuration dict containing network settings
        
    Returns:
        Dict with SSL check results:
        - valid: Whether certificate is valid (bool)
        - issuer: Certificate issuer organization (str)
        - days_until_expiry: Days until certificate expires (int)
        - expires_at: Expiration date ISO format (str)
        - error: Error message if failed (str, optional)
    """
    network_config = config.get('network', {})
    timeout_seconds = network_config.get('request_timeout', 10)
    
    result = {
        'valid': False,
        'issuer': None,
        'days_until_expiry': None,
        'expires_at': None
    }
    
    try:
        # Run the blocking SSL check in a thread pool
        loop = asyncio.get_event_loop()
        cert_info = await loop.run_in_executor(
            None, 
            _get_ssl_certificate, 
            domain, 
            timeout_seconds
        )
        
        if cert_info:
            result['valid'] = True
            result['issuer'] = cert_info.get('issuer')
            result['expires_at'] = cert_info.get('expires_at')
            result['days_until_expiry'] = cert_info.get('days_until_expiry')
        else:
            result['error'] = "Could not retrieve certificate"
            
    except Exception as e:
        result['error'] = f"SSL check error: {str(e)}"
    
    return result


def _get_ssl_certificate(domain: str, timeout: int) -> Dict[str, Any]:
    """
    Synchronous helper to get SSL certificate info.
    This runs in a thread pool to avoid blocking the async event loop.
    """
    context = ssl.create_default_context()
    
    try:
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Extract issuer organization
                issuer = dict(x[0] for x in cert.get('issuer', ()))
                issuer_org = issuer.get('organizationName', 'Unknown')
                
                # Parse expiration date
                not_after = cert.get('notAfter')
                if not_after:
                    # Convert from 'Jan  1 00:00:00 2026 GMT' format
                    expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                    
                    # Calculate days until expiry
                    now = datetime.now(timezone.utc)
                    days_left = (expiry_date - now).days
                    
                    return {
                        'issuer': issuer_org,
                        'expires_at': expiry_date.isoformat(),
                        'days_until_expiry': days_left
                    }
                    
    except socket.timeout:
        raise Exception(f"Connection timeout after {timeout}s")
    except ssl.SSLError as e:
        raise Exception(f"SSL error: {str(e)}")
    except socket.gaierror:
        raise Exception("DNS resolution failed")
    except Exception as e:
        raise Exception(f"Connection error: {str(e)}")
    
    return None
