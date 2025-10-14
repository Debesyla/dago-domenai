"""
Redirect Check - v0.5
Follows HTTP redirect chain and reports the path.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List
from src.utils.logger import safe_run_async


@safe_run_async
async def run_redirect_check(domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Follow redirect chain for a domain.
    
    Args:
        domain: The domain to check (without protocol)
        config: Configuration dict containing network settings
        
    Returns:
        Dict with redirect check results:
        - chain: List of URLs in redirect chain (list of str)
        - length: Number of redirects (int)
        - final_url: Final destination URL (str)
        - error: Error message if failed (str, optional)
    """
    network_config = config.get('network', {})
    timeout_seconds = network_config.get('request_timeout', 10)
    user_agent = network_config.get('user_agent', 'dago-domenai/0.5')
    max_hops = config.get('checks', {}).get('redirect', {}).get('max_hops', 10)
    
    # Start with https
    url = f"https://{domain}"
    
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {'User-Agent': user_agent}
    
    result = {
        'chain': [],
        'length': 0,
        'final_url': None
    }
    
    try:
        # Use a custom redirect handler to track the chain
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            current_url = url
            redirect_count = 0
            
            # Manually follow redirects to track the chain
            while redirect_count < max_hops:
                result['chain'].append(current_url)
                
                async with session.get(current_url, allow_redirects=False) as response:
                    # Check if it's a redirect
                    if response.status in (301, 302, 303, 307, 308):
                        redirect_count += 1
                        location = response.headers.get('Location')
                        if not location:
                            break
                        
                        # Handle relative URLs
                        if location.startswith('/'):
                            from urllib.parse import urljoin
                            current_url = urljoin(current_url, location)
                        elif location.startswith('http'):
                            current_url = location
                        else:
                            # Relative path without leading /
                            from urllib.parse import urljoin
                            current_url = urljoin(current_url, location)
                    else:
                        # No more redirects
                        result['final_url'] = current_url
                        break
            
            # If we exited due to max_hops, final_url is the last one we tried
            if not result['final_url'] and current_url:
                result['final_url'] = current_url
                
            result['length'] = redirect_count
            
    except asyncio.TimeoutError:
        result['error'] = f"Request timeout after {timeout_seconds}s"
    except aiohttp.ClientError as e:
        result['error'] = f"Connection error: {type(e).__name__}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result
