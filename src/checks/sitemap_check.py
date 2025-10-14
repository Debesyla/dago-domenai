"""
Sitemap Check - v0.5
Fetches and validates sitemap.xml file.
"""

import aiohttp
import asyncio
from typing import Dict, Any
from src.utils.logger import safe_run_async


@safe_run_async
async def run_sitemap_check(domain: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for sitemap.xml and count URLs.
    
    Args:
        domain: The domain to check (without protocol)
        config: Configuration dict containing network settings
        
    Returns:
        Dict with sitemap check results:
        - found: Whether sitemap exists (bool)
        - url: URL of the sitemap (str)
        - count_urls: Number of URLs found (int)
        - valid: Whether the XML is parseable (bool)
        - error: Error message if failed (str, optional)
    """
    network_config = config.get('network', {})
    timeout_seconds = network_config.get('request_timeout', 10)
    user_agent = network_config.get('user_agent', 'dago-domenai/0.5')
    
    # Try common sitemap locations
    sitemap_paths = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap']
    
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {'User-Agent': user_agent}
    
    result = {
        'found': False,
        'url': None,
        'count_urls': 0,
        'valid': False
    }
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Try each common sitemap location
            for path in sitemap_paths:
                url = f"https://{domain}{path}"
                
                try:
                    async with session.get(url, allow_redirects=True) as response:
                        if response.status == 200:
                            result['found'] = True
                            result['url'] = url
                            content = await response.text()
                            
                            # Simple URL counting - count <loc> tags
                            try:
                                result['count_urls'] = content.count('<loc>')
                                result['valid'] = '<urlset' in content or '<sitemapindex' in content
                                break  # Found a sitemap, stop searching
                            except Exception as parse_error:
                                result['error'] = f"Parse error: {str(parse_error)}"
                                result['valid'] = False
                except aiohttp.ClientError:
                    # This path didn't work, try the next one
                    continue
                    
    except asyncio.TimeoutError:
        result['error'] = f"Request timeout after {timeout_seconds}s"
    except aiohttp.ClientError as e:
        result['error'] = f"Connection error: {type(e).__name__}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result
