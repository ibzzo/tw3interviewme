import requests
from typing import List, Dict
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SearxSearchService:
    """Service for web searching using public Searx instances."""
    
    def __init__(self):
        # List of public Searx instances (updated for 2025)
        self.searx_instances = [
            "https://searx.be",
            "https://searx.info", 
            "https://searxng.online",
            "https://search.sapti.me",
            "https://search.bus-hit.me",
            "https://searx.work"
        ]
        self.current_instance = 0
        self.max_results = settings.MAX_SEARCH_RESULTS
    
    def get_next_instance(self):
        """Rotate through Searx instances."""
        instance = self.searx_instances[self.current_instance]
        self.current_instance = (self.current_instance + 1) % len(self.searx_instances)
        return instance
    
    def search(self, query: str) -> List[Dict]:
        """
        Search using public Searx instances.
        
        Args:
            query: The search query
            
        Returns:
            List of search results with title, url, and content
        """
        # Try multiple instances in case one fails
        for attempt in range(3):
            instance = self.get_next_instance()
            
            try:
                # Searx API endpoint
                search_url = f"{instance}/search"
                
                params = {
                    'q': query,
                    'format': 'json',
                    'categories': 'general',
                    'language': 'all',
                    'time_range': 'week',  # Focus on recent results
                    'engines': 'google,bing,duckduckgo',  # Use multiple engines
                    'pageno': 1
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; AIBot/1.0)'
                }
                
                response = requests.get(
                    search_url,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Extract results
                    if 'results' in data:
                        for idx, result in enumerate(data['results'][:self.max_results]):
                            formatted_result = {
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'content': result.get('content', '')
                            }
                            
                            # Clean up content
                            if formatted_result['content']:
                                formatted_result['content'] = formatted_result['content'].strip()
                            
                            results.append(formatted_result)
                    
                    logger.info(f"Searx ({instance}): Found {len(results)} results for '{query}'")
                    return results
                    
                else:
                    logger.warning(f"Searx instance {instance} returned {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Searx error with {instance}: {str(e)}")
                continue
        
        # If all instances fail, return empty results
        logger.error("All Searx instances failed")
        return []
    
    def search_news(self, query: str) -> List[Dict]:
        """
        Search specifically for news using Searx.
        """
        # Try with news category
        instance = self.get_next_instance()
        
        try:
            search_url = f"{instance}/search"
            
            params = {
                'q': query,
                'format': 'json',
                'categories': 'news',
                'time_range': 'day',  # Very recent news
                'engines': 'google_news,bing_news',
                'pageno': 1
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AIBot/1.0)'
            }
            
            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'results' in data:
                    for result in data['results'][:self.max_results]:
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'published': result.get('publishedDate', '')
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Searx news search error: {str(e)}")
        
        # Fallback to general search
        return self.search(query)