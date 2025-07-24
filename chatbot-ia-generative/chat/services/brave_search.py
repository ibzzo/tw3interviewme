import requests
import os
from typing import List, Dict
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BraveSearchService:
    """Service for web searching using Brave Search API."""
    
    def __init__(self):
        # Get API key from environment or use a free demo key
        self.api_key = os.environ.get('BRAVE_API_KEY', 'BSAQz5B1PECaTq7bVzpQc6fKrBMcL_m')  # Demo key for testing
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.max_results = settings.MAX_SEARCH_RESULTS
    
    def search(self, query: str) -> List[Dict]:
        """
        Search the web using Brave Search API.
        
        Args:
            query: The search query
            
        Returns:
            List of search results with title, url, and content
        """
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": self.max_results,
                "freshness": "pw",  # Past week for recent results
                "text_decorations": False,
                "result_filter": "web"
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Extract web results
                if 'web' in data and 'results' in data['web']:
                    for result in data['web']['results']:
                        formatted_result = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('description', '')
                        }
                        
                        # Add extra context if available
                        if 'extra_snippets' in result:
                            extra = ' '.join(result['extra_snippets'])
                            formatted_result['content'] += f" {extra}"
                        
                        results.append(formatted_result)
                
                logger.info(f"Brave Search: Found {len(results)} results for '{query}'")
                return results
            else:
                logger.error(f"Brave Search API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Brave Search error: {str(e)}")
            return []
    
    def search_with_ai_snippets(self, query: str) -> Dict:
        """
        Enhanced search that includes AI-generated summaries.
        
        Returns both search results and an AI summary if available.
        """
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": self.max_results,
                "freshness": "pw",
                "summary": True  # Request AI summary
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = self.search(query)  # Get regular results
                
                # Extract AI summary if available
                summary = None
                if 'summarizer' in data and 'summary' in data['summarizer']:
                    summary = data['summarizer']['summary']
                
                return {
                    'results': results,
                    'summary': summary
                }
            else:
                return {'results': [], 'summary': None}
                
        except Exception as e:
            logger.error(f"Brave enhanced search error: {str(e)}")
            return {'results': [], 'summary': None}