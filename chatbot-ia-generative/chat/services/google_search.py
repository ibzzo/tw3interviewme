import requests
from typing import List, Dict
import logging
from django.conf import settings
import os

logger = logging.getLogger(__name__)


class GoogleSearchService:
    """Service for web searching using Google Custom Search API (100 free queries/day)."""
    
    def __init__(self):
        # You need to get these from Google Cloud Console
        # For demo, using a test key (replace with your own)
        self.api_key = os.environ.get('GOOGLE_API_KEY', 'AIzaSyDRqPI0WYQ7lUKiI3QjJKDG7sBSvTnWyWo')
        self.search_engine_id = os.environ.get('GOOGLE_CX', '017576662512468239146:omuauf_lfve')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.max_results = settings.MAX_SEARCH_RESULTS
    
    def search(self, query: str) -> List[Dict]:
        """
        Search using Google Custom Search API.
        
        Args:
            query: The search query
            
        Returns:
            List of search results with title, url, and content
        """
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': self.max_results,
                'dateRestrict': 'w1',  # Results from last week
                'sort': 'date'  # Sort by date
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'items' in data:
                    for item in data['items']:
                        formatted_result = {
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'content': item.get('snippet', '')
                        }
                        
                        # Add extra content from page maps if available
                        if 'pagemap' in item and 'metatags' in item['pagemap']:
                            metatags = item['pagemap']['metatags'][0]
                            if 'og:description' in metatags:
                                formatted_result['content'] = metatags['og:description']
                        
                        results.append(formatted_result)
                
                logger.info(f"Google Search: Found {len(results)} results for '{query}'")
                return results
                
            elif response.status_code == 429:
                logger.error("Google Search API quota exceeded")
                return []
            else:
                logger.error(f"Google Search API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Google Search error: {str(e)}")
            return []
    
    def search_news(self, query: str) -> List[Dict]:
        """Search specifically for news."""
        # Add news-specific parameters
        return self.search(f"{query} news latest developments")