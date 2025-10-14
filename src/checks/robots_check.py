"""
Robots.txt Check - v0.5
Fetches and parses robots.txt file.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List
from src.utils.logger import safe_run_async


@safe_run_async
async def run_robots_check(domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for robots.txt and parse basic rules.
    
    Args:
        domain: The domain to check (without protocol)
        config: Configuration dict containing network settings
        
    Returns:
        Dict with robots check results:
        - found: Whether robots.txt exists (bool)
        - allow: List of allowed paths (list of str)
        - disallow: List of disallowed paths (list of str)
        - valid: Whether the file is parseable (bool)
        - error: Error message if failed (str, optional)
    """
    network_config = config.get('network', {})
    timeout_seconds = network_config.get('request_timeout', 10)
    user_agent = network_config.get('user_agent', 'dago-domenai/0.5')
    
    url = f"https://{domain}/robots.txt"
    
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {'User-Agent': user_agent}
    
    result = {
        'found': False,
        'allow': [],
        'disallow': [],
        'valid': False
    }
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    result['found'] = True
                    content = await response.text()
                    
                    # Simple parsing - look for Allow and Disallow lines
                    try:
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.lower().startswith('allow:'):
                                path = line.split(':', 1)[1].strip()
                                if path:
                                    result['allow'].append(path)
                            elif line.lower().startswith('disallow:'):
                                path = line.split(':', 1)[1].strip()
                                if path:
                                    result['disallow'].append(path)
                        
                        result['valid'] = True
                    except Exception as parse_error:
                        result['error'] = f"Parse error: {str(parse_error)}"
                        result['valid'] = False
                else:
                    result['found'] = False
                    
    except asyncio.TimeoutError:
        result['error'] = f"Request timeout after {timeout_seconds}s"
    except aiohttp.ClientError as e:
        result['error'] = f"Connection error: {type(e).__name__}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result
