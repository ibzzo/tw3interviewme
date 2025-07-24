from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import logging
from django.conf import settings
from chat.models import SearchCache
from django.utils import timezone
import asyncio

logger = logging.getLogger(__name__)


class SearchService:
    """Service for web searching using DuckDuckGo."""
    
    def __init__(self):
        self.max_results = settings.MAX_SEARCH_RESULTS
        self.timeout = settings.SEARCH_TIMEOUT
        self.cache_hours = 24  # Cache search results for 24 hours
    
    async def search(self, query: str, use_cache: bool = True) -> List[Dict]:
        """
        Search the web for information.
        
        Args:
            query: The search query
            use_cache: Whether to use cached results if available
            
        Returns:
            List of search results with title, url, and content
        """
        
        # Check cache first if enabled
        if use_cache:
            cached_results = await self._get_cached_results(query)
            if cached_results:
                logger.info(f"Using cached results for query: {query}")
                return cached_results
        
        try:
            # Run the synchronous search in a thread pool
            results = await asyncio.get_event_loop().run_in_executor(
                None, 
                self._perform_search, 
                query
            )
            
            # Cache the results
            if results and use_cache:
                await self._cache_results(query, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Search error for query '{query}': {str(e)}")
            return []
    
    def _perform_search(self, query: str) -> List[Dict]:
        """Perform the actual search using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = []
                
                # Search and get results
                search_results = ddgs.text(
                    query, 
                    max_results=self.max_results,
                    timelimit='m'  # Last month
                )
                
                for result in search_results:
                    formatted_result = {
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),
                        'content': result.get('body', '')[:500]  # Limit content length
                    }
                    results.append(formatted_result)
                
                logger.info(f"Found {len(results)} results for query: {query}")
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    async def _get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results if available and not expired."""
        try:
            cache_entry = await SearchCache.objects.filter(query=query).afirst()
            if cache_entry and not cache_entry.is_expired(self.cache_hours):
                return cache_entry.results
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")
        return None
    
    async def _cache_results(self, query: str, results: List[Dict]):
        """Cache search results."""
        try:
            await SearchCache.objects.aupdate_or_create(
                query=query,
                defaults={'results': results, 'created_at': timezone.now()}
            )
        except Exception as e:
            logger.error(f"Cache storage error: {str(e)}")
    
    def extract_key_info(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Extract and summarize key information from search results.
        This method can be enhanced with NLP techniques.
        """
        
        # For now, just return the top results with some filtering
        filtered_results = []
        
        for result in results[:3]:  # Top 3 results
            if result['title'] and result['content']:
                filtered_results.append({
                    'title': result['title'],
                    'url': result['url'],
                    'content': result['content'],
                    'relevance': self._calculate_relevance(query, result)
                })
        
        # Sort by relevance
        filtered_results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return filtered_results
    
    def _calculate_relevance(self, query: str, result: Dict) -> float:
        """
        Simple relevance calculation based on keyword matching.
        This can be enhanced with more sophisticated NLP techniques.
        """
        query_words = query.lower().split()
        content = (result['title'] + ' ' + result['content']).lower()
        
        matches = sum(1 for word in query_words if word in content)
        relevance = matches / len(query_words) if query_words else 0
        
        return relevance