"""
HTTP Status Check - v0.4
Fetches the HTTP status code for a domain.
"""

import aiohttp
import asyncio
from typing import Dict, Any
from src.utils.logger import safe_run_async


@safe_run_async
async def run_status_check(domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform HTTP status check on a domain.
    
    Args:
        domain: The domain to check (without protocol)
        config: Configuration dict containing network settings
        
    Returns:
        Dict with check results:
        - code: HTTP status code (int)
        - ok: Whether request was successful (bool)
        - final_url: Final URL after redirects (str)
        - duration_ms: Request duration in milliseconds (int)
        - error: Error message if failed (str, optional)
    """
    network_config = config.get('network', {})
    timeout_seconds = network_config.get('request_timeout', 10)
    user_agent = network_config.get('user_agent', 'dago-domenai/0.4')
    
    # Prepare URL with https:// protocol
    url = f"https://{domain}"
    
    # Configure timeout and headers
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {'User-Agent': user_agent}
    
    result = {
        'code': None,
        'ok': False,
        'final_url': None,
        'duration_ms': None
    }
    
    try:
        # Record start time
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                # Record end time
                end_time = asyncio.get_event_loop().time()
                duration_ms = int((end_time - start_time) * 1000)
                
                result['code'] = response.status
                result['ok'] = response.status < 400
                result['final_url'] = str(response.url)
                result['duration_ms'] = duration_ms
                
    except asyncio.TimeoutError:
        result['error'] = f"Request timeout after {timeout_seconds}s"
    except aiohttp.ClientError as e:
        result['error'] = f"Connection error: {type(e).__name__}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result
