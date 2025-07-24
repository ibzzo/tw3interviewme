import httpx
import json
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Chatbot with Search"
        }
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        search_results: Optional[List[Dict]] = None
    ) -> str:
        """Generate a response using OpenRouter API with optional search results."""
        
        try:
            # If search results are provided, add them to the system message
            if search_results:
                search_context = self._format_search_results(search_results)
                system_message = {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant with access to web search results. 
                    Use the following search results to provide accurate and up-to-date information:
                    
                    {search_context}
                    
                    Always cite your sources when using information from search results."""
                }
                # Insert system message at the beginning
                messages = [system_message] + messages
            
            # Prepare the request
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            # Make the API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error: {response.status_code}")
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
        except httpx.TimeoutException:
            logger.error("OpenRouter API timeout")
            raise Exception("The AI service is taking too long to respond. Please try again.")
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise Exception(f"Error generating response: {str(e)}")
    
    def _format_search_results(self, search_results: List[Dict]) -> str:
        """Format search results into a readable string for the LLM."""
        formatted_results = []
        
        for i, result in enumerate(search_results, 1):
            formatted_result = f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')}
---"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)