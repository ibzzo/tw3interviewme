import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from tavily import TavilyClient
from django.conf import settings
from chat.models import SearchCache
import json

logger = logging.getLogger(__name__)


class TavilySearchService:
    """Service de recherche web optimisé avec Tavily API - Conçu spécifiquement pour les agents IA."""
    
    def __init__(self):
        # Utiliser une clé d'essai gratuite si pas de clé dans l'environnement
        self.api_key = os.environ.get('TAVILY_API_KEY', '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')
        self.client = TavilyClient(api_key=self.api_key)
        self.max_results = getattr(settings, 'MAX_SEARCH_RESULTS', 5)
        
    def search(self, query: str, search_type: str = 'news', use_cache: bool = True) -> List[Dict]:
        """
        Recherche intelligente avec Tavily API.
        
        Args:
            query: La requête de recherche
            search_type: Type de recherche ('news', 'general', 'technical')
            use_cache: Utiliser le cache ou non
            
        Returns:
            Liste des résultats pertinents
        """
        logger.info(f"\n🔍 TAVILY API - RECHERCHE INTELLIGENTE")
        logger.info(f"📝 Query: {query}")
        logger.info(f"🎯 Type: {search_type}")
        
        # Vérifier le cache
        if use_cache:
            cached = self._get_cached_results(query)
            if cached:
                logger.info(f"📦 Utilisation du cache pour: {query[:50]}...")
                return cached
                
        try:
            # Configuration selon le type de recherche
            search_params = self._get_search_params(query, search_type)
            
            # Effectuer la recherche
            logger.info(f"🌐 Appel API Tavily avec params: {search_params}")
            response = self.client.search(**search_params)
            
            # Traiter les résultats
            results = self._process_results(response, query)
            
            # Mettre en cache si on a des résultats
            if results and use_cache:
                self._cache_results(query, results)
                
            logger.info(f"✅ {len(results)} résultats pertinents trouvés")
            
            # Afficher les résultats dans la console pour debug
            if results:
                logger.info("\n" + "🔍"*40)
                logger.info("🎯 RÉSULTATS TAVILY API")
                logger.info("🔍"*40)
                for i, r in enumerate(results):
                    logger.info(f"\n📌 Résultat {i+1}:")
                    logger.info(f"   📝 Titre: {r['title']}")
                    logger.info(f"   🌐 URL: {r['url']}")
                    logger.info(f"   🏢 Source: {r['source']}")
                    logger.info(f"   📅 Date: {r.get('date', 'N/A')}")
                    logger.info(f"   📊 Score: {r.get('relevance_score', 0):.1%}")
                    logger.info(f"   🏷️ Tags: {', '.join(r.get('tags', []))}")
                    logger.info(f"   💬 Contenu: {r['content'][:200]}...")
                logger.info("🔍"*40 + "\n")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur Tavily API: {str(e)}")
            # Fallback vers SerpAPI si disponible
            return self._fallback_to_serpapi(query)
    
    def _get_search_params(self, query: str, search_type: str) -> Dict:
        """Configure les paramètres de recherche selon le type."""
        
        # Configuration de base
        params = {
            "query": query,
            "max_results": 10,  # On récupère plus pour filtrer ensuite
            "include_domains": [],
            "exclude_domains": [],
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False
        }
        
        # Personnalisation selon le type
        if search_type == 'news':
            # Pour les actualités, on veut des sources fiables et récentes
            params["query"] = f"{query} latest news announcements developments 2025"
            params["search_depth"] = "advanced"
            params["topic"] = "news"
            params["days"] = 7  # Derniers 7 jours
            params["include_domains"] = [
                "openai.com", "anthropic.com", "google.com", "microsoft.com",
                "techcrunch.com", "theverge.com", "wired.com", "venturebeat.com",
                "arstechnica.com", "thenextweb.com", "forbes.com"
            ]
            
        elif search_type == 'technical':
            # Pour les recherches techniques
            params["query"] = f"{query} implementation tutorial code example"
            params["search_depth"] = "advanced"
            params["include_domains"] = [
                "github.com", "stackoverflow.com", "medium.com", "dev.to",
                "huggingface.co", "arxiv.org", "papers.nips.cc"
            ]
            
        else:  # general
            params["search_depth"] = "basic"
            
        return params
    
    def _process_results(self, response: Dict, query: str) -> List[Dict]:
        """Traite et enrichit les résultats de Tavily."""
        processed_results = []
        
        # Ajouter la réponse IA si disponible
        if response.get("answer"):
            processed_results.append({
                'title': "Résumé IA par Tavily",
                'url': f"https://tavily.com/search?q={query.replace(' ', '+')}",
                'content': response["answer"],
                'source': "Tavily AI",
                'date': datetime.now().strftime("%Y-%m-%d"),
                'relevance_score': 1.0,
                'tags': ['AI Summary', 'Tavily'],
                'is_ai_summary': True
            })
        
        # Traiter les résultats individuels
        if response.get("results"):
            for idx, result in enumerate(response["results"]):
                # Calculer le score de pertinence
                relevance_score = self._calculate_relevance_score(result, query)
                
                # Extraire les informations
                processed_result = {
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'source': self._extract_domain(result.get('url', '')),
                    'date': result.get('published_date', ''),
                    'relevance_score': relevance_score,
                    'tags': self._extract_tags(result),
                    'score': result.get('score', 0)  # Score natif de Tavily
                }
                
                # Enrichir avec les données supplémentaires si disponibles
                if result.get('raw_content'):
                    processed_result['raw_content'] = result['raw_content'][:500]
                    
                processed_results.append(processed_result)
        
        # Trier par pertinence (combinaison du score Tavily et notre score)
        processed_results.sort(
            key=lambda x: (x.get('is_ai_summary', False), x['relevance_score'], x.get('score', 0)), 
            reverse=True
        )
        
        return processed_results[:self.max_results]
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calcule un score de pertinence personnalisé."""
        score = result.get('score', 0.5)  # Score de base de Tavily
        
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        url = result.get('url', '').lower()
        query_lower = query.lower()
        
        # Bonus pour correspondance exacte
        if query_lower in title:
            score += 0.2
        if query_lower in content:
            score += 0.1
            
        # Bonus pour sources fiables en IA
        ai_domains = [
            'openai.com', 'anthropic.com', 'google.com/ai', 'microsoft.com/ai',
            'huggingface.co', 'arxiv.org', 'deepmind.com'
        ]
        if any(domain in url for domain in ai_domains):
            score += 0.2
            
        # Bonus pour contenu récent (si date disponible)
        if result.get('published_date'):
            try:
                # Analyser la fraîcheur
                date_str = result['published_date']
                if '2025' in date_str:
                    score += 0.3
                elif '2024' in date_str and any(month in date_str for month in ['Dec', 'Nov', 'Oct']):
                    score += 0.2
            except:
                pass
                
        # Bonus pour mots-clés d'actualité
        news_keywords = [
            'announces', 'launches', 'releases', 'unveils', 'introduces',
            'annonce', 'lance', 'dévoile', 'présente', 'nouveau'
        ]
        if any(keyword in title or keyword in content for keyword in news_keywords):
            score += 0.15
            
        return min(score, 1.0)
    
    def _extract_tags(self, result: Dict) -> List[str]:
        """Extrait des tags pertinents du résultat."""
        tags = []
        content = (result.get('title', '') + ' ' + result.get('content', '')).lower()
        
        # Tags IA spécifiques
        ai_tags = {
            'openai': 'OpenAI', 'gpt': 'GPT', 'chatgpt': 'ChatGPT',
            'anthropic': 'Anthropic', 'claude': 'Claude',
            'google': 'Google AI', 'gemini': 'Gemini', 'bard': 'Bard',
            'microsoft': 'Microsoft', 'copilot': 'Copilot',
            'llm': 'LLM', 'transformer': 'Transformer',
            'generative ai': 'Generative AI', 'ia générative': 'IA Générative'
        }
        
        for keyword, tag in ai_tags.items():
            if keyword in content:
                tags.append(tag)
                
        return list(set(tags))[:5]  # Max 5 tags uniques
    
    def _extract_domain(self, url: str) -> str:
        """Extrait le domaine d'une URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return 'Unknown'
    
    def _get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """Récupère les résultats en cache."""
        try:
            cache_entry = SearchCache.objects.filter(query=query).first()
            # Cache de 2h pour Tavily (résultats très frais)
            if cache_entry and not cache_entry.is_expired(2):
                return cache_entry.results
        except Exception as e:
            logger.error(f"Erreur cache: {e}")
        return None
    
    def _cache_results(self, query: str, results: List[Dict]):
        """Met en cache les résultats."""
        try:
            SearchCache.objects.update_or_create(
                query=query,
                defaults={'results': results}
            )
        except Exception as e:
            logger.error(f"Erreur mise en cache: {e}")
    
    def _fallback_to_serpapi(self, query: str) -> List[Dict]:
        """Fallback vers SerpAPI si Tavily échoue."""
        try:
            from .serpapi_service import SerpAPIService
            logger.warning("⚠️ Fallback vers SerpAPI")
            serpapi = SerpAPIService()
            return serpapi.search(query)
        except:
            return []
    
    def get_trending_ai_topics(self) -> List[Dict]:
        """Récupère les sujets tendances en IA."""
        try:
            # Recherche spéciale pour les tendances
            response = self.client.search(
                query="artificial intelligence latest trending topics today",
                search_depth="advanced",
                topic="news",
                max_results=10,
                days=1
            )
            
            topics = []
            if response.get("results"):
                for result in response["results"][:5]:
                    topics.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'trend': 'hot',
                        'source': self._extract_domain(result.get('url', ''))
                    })
                    
            return topics
            
        except Exception as e:
            logger.error(f"Erreur trending topics: {e}")
            return []