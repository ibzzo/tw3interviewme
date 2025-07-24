import os
from serpapi import GoogleSearch
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
from django.conf import settings
from chat.models import SearchCache
import re
import json

logger = logging.getLogger(__name__)


class SerpAPIService:
    """Service intelligent pour recherche web via SerpAPI avec optimisations avancées."""
    
    def __init__(self):
        self.api_key = os.environ.get('SERPAPI_KEY', '8ba4cd7cae7dab8bab44ee1ea895b405552d5b956d2b725122084e5a081eaf9f')
        self.max_results = settings.MAX_SEARCH_RESULTS
        
        # Stratégies de recherche par type de requête
        self.search_strategies = {
            'news': self._search_news_strategy,
            'technical': self._search_technical_strategy,
            'general': self._search_general_strategy,
            'academic': self._search_academic_strategy
        }
    
    def analyze_query_intent(self, query: str) -> Dict[str, any]:
        """Analyse l'intention de la requête pour optimiser la recherche."""
        query_lower = query.lower()
        
        # Détection du type de recherche
        if any(word in query_lower for word in ['derniers', 'récents', 'news', 'actualités', 'cette semaine', 'aujourd\'hui', 'latest', 'recent', 'annoncés', 'développements']):
            search_type = 'news'
            time_filter = 'd'  # Dernières 24h pour plus de fraîcheur
        elif any(word in query_lower for word in ['comment', 'tutoriel', 'how to', 'guide', 'implementation']):
            search_type = 'technical'
            time_filter = 'm'  # Dernier mois
        elif any(word in query_lower for word in ['recherche', 'étude', 'paper', 'research', 'academic']):
            search_type = 'academic'
            time_filter = 'y'  # Dernière année
        else:
            search_type = 'general'
            time_filter = None
        
        # Extraction des mots-clés importants
        keywords = self._extract_keywords(query)
        
        # Détection de la langue
        language = 'fr' if any(word in query_lower for word in ['quels', 'comment', 'pourquoi', 'développements']) else 'en'
        
        return {
            'type': search_type,
            'time_filter': time_filter,
            'keywords': keywords,
            'language': language,
            'original_query': query
        }
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrait les mots-clés importants de la requête."""
        # Mots à ignorer
        stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'mais',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'quels', 'sont', 'what', 'are', 'is', 'how', 'comment', 'pourquoi'
        }
        
        # Extraction des mots importants
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Prioriser les mots techniques/spécifiques
        tech_terms = ['ia', 'ai', 'générative', 'generative', 'llm', 'gpt', 'claude', 
                      'machine learning', 'deep learning', 'neural', 'transformer']
        
        important_keywords = [k for k in keywords if any(term in k for term in tech_terms)]
        
        return important_keywords[:5] if important_keywords else keywords[:5]
    
    def search(self, query: str, search_type: str = None, use_cache: bool = True) -> List[Dict]:
        """
        Recherche intelligente avec SerpAPI.
        """
        logger.info(f"\n🔍 SERPAPI - RECHERCHE INTELLIGENTE")
        
        # Vérifier le cache
        if use_cache:
            cached = self._get_cached_results(query)
            if cached:
                logger.info(f"📦 Utilisation du cache pour: {query[:50]}...")
                return cached
        
        # Analyser l'intention de la requête
        intent = self.analyze_query_intent(query)
        # Override avec search_type si fourni
        if search_type:
            intent['type'] = search_type
        logger.info(f"🧠 Analyse: Type={intent['type']}, Langue={intent['language']}, Mots-clés={intent['keywords']}")
        
        # Utiliser la stratégie appropriée
        strategy = self.search_strategies.get(intent['type'], self._search_general_strategy)
        results = strategy(intent)
        
        # Enrichir et scorer les résultats
        if results:
            results = self._enrich_and_score_results(results, intent)
            
            # Afficher les résultats dans la console pour debug
            logger.info("\n" + "🌎"*40)
            logger.info("🎯 RÉSULTATS SERPAPI")
            logger.info("🌎"*40)
            for i, r in enumerate(results):
                logger.info(f"\n📌 Résultat {i+1}:")
                logger.info(f"   📝 Titre: {r['title']}")
                logger.info(f"   🌐 URL: {r['url']}")
                logger.info(f"   🏢 Source: {r['source']}")
                logger.info(f"   📅 Date: {r.get('date', 'N/A')}")
                logger.info(f"   📊 Score: {r.get('relevance_score', 0):.1%}")
                logger.info(f"   🏷️ Tags: {', '.join(r.get('tags', []))}")
                logger.info(f"   💬 Contenu: {r['content'][:200]}...")
            logger.info("🌎"*40 + "\n")
            
            # Mettre en cache
            if use_cache:
                self._cache_results(query, results)
        
        return results
    
    def _search_news_strategy(self, intent: Dict) -> List[Dict]:
        """Stratégie optimisée pour les actualités."""
        logger.info(f"📰 Stratégie NEWS activée")
        
        # Requêtes multiples pour couvrir différents angles
        queries = [
            # Requête principale ciblée sur les annonces récentes
            f"\"AI announcements\" OR \"IA annonces\" {intent['original_query']} -filetype:pdf",
            # Requête spécifique aux grandes entreprises
            f"(OpenAI OR Anthropic OR Google OR Microsoft OR Meta) AI announcement 2025",
            # Requête sur les modèles spécifiques
            f"GPT-5 OR Claude-3 OR Gemini OR LLaMA new model release 2025"
        ]
        
        all_results = []
        
        for query in queries:
            params = {
                "q": query,
                "api_key": self.api_key,
                "tbm": "nws",  # Google News
                "tbs": "qdr:w,sbd:1",  # Dernière semaine, triés par date
                "num": 20,  # Plus de résultats pour filtrer
                "hl": intent['language'],
                "gl": "fr" if intent['language'] == 'fr' else "us"
            }
        
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if "news_results" in results:
                    for item in results["news_results"]:
                        # Éviter les doublons
                        if not any(r['url'] == item.get('link', '') for r in all_results):
                            date_parsed = self._parse_serpapi_date(item.get('date', ''))
                            all_results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'content': item.get('snippet', ''),
                                'source': item.get('source', {}).get('name', '') if isinstance(item.get('source'), dict) else item.get('source', ''),
                                'date': item.get('date', ''),
                                'date_parsed': date_parsed.isoformat() if date_parsed else None,
                                'relevance_score': self._calculate_news_relevance(item, intent)
                            })
            except Exception as e:
                logger.error(f"❌ Erreur pour requête '{query[:50]}...': {str(e)}")
        
        # Si pas assez de résultats news, chercher aussi dans les résultats web récents
        if len(all_results) < 5:
            logger.info("🔄 Recherche complémentaire dans les résultats web")
            web_params = {
                "q": f'{intent["original_query"]} "announced today" OR "announced yesterday" OR "launching" AI',
                "api_key": self.api_key,
                "num": 10,
                "tbs": "qdr:d",  # Dernières 24h
                "hl": intent['language']
            }
            
            try:
                search = GoogleSearch(web_params)
                results = search.get_dict()
                
                if "organic_results" in results:
                    for item in results["organic_results"]:
                        # Vérifier si c'est vraiment une actualité récente
                        snippet = item.get('snippet', '').lower()
                        if any(word in snippet for word in ['today', 'yesterday', 'announced', 'launches', 'releases', 'introduces']):
                            date_parsed = datetime.now() - timedelta(hours=12)  # Estimation récente
                            all_results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'content': item.get('snippet', ''),
                                'source': self._extract_domain(item.get('link', '')),
                                'date': 'Recent',
                                'date_parsed': date_parsed.isoformat(),
                                'relevance_score': self._calculate_news_relevance(item, intent) * 0.9  # Légèrement moins pertinent
                            })
            except Exception as e:
                logger.error(f"❌ Erreur recherche web complémentaire: {str(e)}")
        
        # Trier par pertinence et date
        all_results.sort(key=lambda x: (x['relevance_score'], self._parse_date_priority(x.get('date', ''))), reverse=True)
        
        # Dédupliquer et prendre les meilleurs
        unique_results = []
        seen_titles = set()
        for result in all_results:
            title_key = result['title'][:50].lower()
            if title_key not in seen_titles:
                unique_results.append(result)
                seen_titles.add(title_key)
        
        logger.info(f"✅ {len(unique_results)} actualités uniques trouvées")
        return unique_results[:self.max_results]
    
    def _search_technical_strategy(self, intent: Dict) -> List[Dict]:
        """Stratégie pour recherches techniques/tutoriels."""
        logger.info(f"🔧 Stratégie TECHNIQUE activée")
        
        # Ajouter des sites techniques de référence
        tech_sites = "site:github.com OR site:stackoverflow.com OR site:medium.com OR site:dev.to"
        enhanced_query = f"{intent['original_query']} tutorial implementation code {tech_sites}"
        
        params = {
            "q": enhanced_query,
            "api_key": self.api_key,
            "num": 10,
            "hl": intent['language']
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            formatted_results = []
            if "organic_results" in results:
                for item in results["organic_results"]:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', ''),
                        'source': self._extract_domain(item.get('link', '')),
                        'relevance_score': self._calculate_relevance(item, intent)
                    })
            
            # Prioriser GitHub et StackOverflow
            formatted_results.sort(key=lambda x: (
                x['relevance_score'],
                'github.com' in x['url'],
                'stackoverflow.com' in x['url']
            ), reverse=True)
            
            logger.info(f"✅ {len(formatted_results)} résultats techniques trouvés")
            return formatted_results[:self.max_results]
            
        except Exception as e:
            logger.error(f"❌ Erreur SerpAPI Technical: {str(e)}")
            return []
    
    def _search_general_strategy(self, intent: Dict) -> List[Dict]:
        """Stratégie de recherche générale avec AI Overview."""
        logger.info(f"🌐 Stratégie GÉNÉRALE activée")
        
        params = {
            "q": intent['original_query'],
            "api_key": self.api_key,
            "num": 10,
            "hl": intent['language'],
            "gl": "fr" if intent['language'] == 'fr' else "us"
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            formatted_results = []
            
            # Extraire l'AI Overview si disponible
            if "ai_overview" in results:
                logger.info("🤖 AI Overview trouvé!")
                ai_content = results["ai_overview"].get("text", "")
                if ai_content:
                    formatted_results.append({
                        'title': "Résumé IA de Google",
                        'url': "https://google.com",
                        'content': ai_content,
                        'source': "Google AI",
                        'relevance_score': 1.0  # Très pertinent
                    })
            
            # Résultats organiques
            if "organic_results" in results:
                for item in results["organic_results"]:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', ''),
                        'source': self._extract_domain(item.get('link', '')),
                        'relevance_score': self._calculate_relevance(item, intent)
                    })
            
            # Trier par pertinence
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"✅ {len(formatted_results)} résultats généraux trouvés")
            return formatted_results[:self.max_results]
            
        except Exception as e:
            logger.error(f"❌ Erreur SerpAPI General: {str(e)}")
            return []
    
    def _search_academic_strategy(self, intent: Dict) -> List[Dict]:
        """Stratégie pour recherches académiques."""
        logger.info(f"🎓 Stratégie ACADÉMIQUE activée")
        
        # Utiliser Google Scholar
        params = {
            "q": intent['original_query'],
            "api_key": self.api_key,
            "engine": "google_scholar",
            "num": 10,
            "hl": intent['language']
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            formatted_results = []
            if "organic_results" in results:
                for item in results["organic_results"]:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', ''),
                        'source': item.get('publication_info', {}).get('summary', 'Academic'),
                        'relevance_score': self._calculate_relevance(item, intent)
                    })
            
            logger.info(f"✅ {len(formatted_results)} résultats académiques trouvés")
            return formatted_results[:self.max_results]
            
        except Exception as e:
            logger.error(f"❌ Erreur SerpAPI Academic: {str(e)}")
            # Fallback vers recherche générale
            return self._search_general_strategy(intent)
    
    def _calculate_relevance(self, result: Dict, intent: Dict) -> float:
        """Calcule un score de pertinence sophistiqué."""
        score = 0.0
        
        title = result.get('title', '').lower()
        content = result.get('snippet', '').lower()
        url = result.get('link', '').lower()
        
        # Score basé sur les mots-clés
        for keyword in intent['keywords']:
            if keyword in title:
                score += 0.3
            if keyword in content:
                score += 0.2
            if keyword in url:
                score += 0.1
        
        # Bonus pour la fraîcheur (news)
        if intent['type'] == 'news' and 'date' in result:
            try:
                # Favoriser les résultats récents
                date_str = result['date']
                if 'hour' in date_str or 'heure' in date_str:
                    score += 0.3
                elif 'day' in date_str or 'jour' in date_str:
                    score += 0.2
            except:
                pass
        
        # Bonus pour sources fiables
        trusted_sources = ['openai.com', 'anthropic.com', 'google.com', 'microsoft.com', 
                          'github.com', 'arxiv.org', 'nature.com', 'science.org']
        
        if any(source in url for source in trusted_sources):
            score += 0.2
        
        return min(score, 1.0)  # Normaliser entre 0 et 1
    
    def _calculate_news_relevance(self, result: Dict, intent: Dict) -> float:
        """Calcule un score de pertinence spécifique pour les actualités."""
        score = 0.0
        
        title = result.get('title', '').lower()
        content = result.get('snippet', '').lower()
        url = result.get('link', '').lower()
        
        # Mots-clés d'actualité importants
        news_keywords = [
            'announces', 'announced', 'launches', 'launched', 'releases', 'released',
            'introduces', 'unveils', 'reveals', 'debuts', 'new', 'latest',
            'annonce', 'lance', 'dévoile', 'présente', 'nouveau', 'dernière'
        ]
        
        # Score pour mots-clés d'actualité
        for keyword in news_keywords:
            if keyword in title:
                score += 0.2
            if keyword in content:
                score += 0.1
        
        # Score pour entreprises IA majeures
        ai_companies = [
            'openai', 'anthropic', 'google', 'microsoft', 'meta', 'nvidia',
            'hugging face', 'stability ai', 'cohere', 'inflection'
        ]
        
        for company in ai_companies:
            if company in title or company in content:
                score += 0.3
                break
        
        # Score pour modèles IA spécifiques
        ai_models = [
            'gpt', 'claude', 'gemini', 'llama', 'palm', 'bard', 'copilot',
            'stable diffusion', 'midjourney', 'dall-e'
        ]
        
        for model in ai_models:
            if model in title or model in content:
                score += 0.2
                break
        
        # Score pour la fraîcheur
        date_str = result.get('date', '').lower()
        if any(x in date_str for x in ['hour', 'heure', 'minute']):
            score += 0.4  # Très récent
        elif any(x in date_str for x in ['today', "aujourd'hui", '1 day', '1 jour']):
            score += 0.3
        elif any(x in date_str for x in ['yesterday', 'hier', '2 days', '2 jours']):
            score += 0.2
        elif any(x in date_str for x in ['3 days', '3 jours', '4 days', '4 jours']):
            score += 0.1
        
        # Pénalité pour contenus non pertinents
        irrelevant_keywords = ['course', 'tutorial', 'how to', 'guide', 'cours', 'tutoriel']
        if any(keyword in title.lower() for keyword in irrelevant_keywords):
            score *= 0.5
        
        return min(score, 1.0)
    
    def _parse_date_priority(self, date_str: str) -> int:
        """Parse la date pour le tri (plus récent = priorité plus élevée)."""
        date_lower = date_str.lower()
        
        if any(x in date_lower for x in ['minute', 'hour', 'heure']):
            return 10
        elif any(x in date_lower for x in ['today', "aujourd'hui"]):
            return 9
        elif any(x in date_lower for x in ['yesterday', 'hier']):
            return 8
        elif '1 day' in date_lower or '1 jour' in date_lower:
            return 7
        elif '2 day' in date_lower or '2 jour' in date_lower:
            return 6
        elif '3 day' in date_lower or '3 jour' in date_lower:
            return 5
        else:
            return 0
    
    def _enrich_and_score_results(self, results: List[Dict], intent: Dict) -> List[Dict]:
        """Enrichit les résultats avec des métadonnées supplémentaires."""
        enriched = []
        
        for result in results:
            # Ajouter un résumé si le contenu est long
            content = result.get('content', '')
            if len(content) > 200:
                result['summary'] = content[:197] + "..."
            
            # Ajouter des tags basés sur le contenu
            result['tags'] = self._extract_tags(result)
            
            # Score final
            if 'relevance_score' not in result:
                result['relevance_score'] = self._calculate_relevance(result, intent)
            
            enriched.append(result)
        
        # Retourner les meilleurs résultats
        enriched.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return enriched
    
    def _extract_tags(self, result: Dict) -> List[str]:
        """Extrait des tags du contenu."""
        tags = []
        content = (result.get('title', '') + ' ' + result.get('content', '')).lower()
        
        # Tags IA
        ai_tags = {
            'gpt': 'GPT', 'claude': 'Claude', 'gemini': 'Gemini', 
            'llm': 'LLM', 'transformer': 'Transformer', 'bert': 'BERT'
        }
        
        for keyword, tag in ai_tags.items():
            if keyword in content:
                tags.append(tag)
        
        return tags[:3]  # Limiter à 3 tags
    
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
            if cache_entry and not cache_entry.is_expired(6):  # Cache 6h pour SerpAPI
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
    
    def get_trending_topics(self) -> List[Dict]:
        """Récupère les sujets tendances en IA."""
        params = {
            "q": "artificial intelligence latest news",
            "api_key": self.api_key,
            "tbm": "nws",
            "num": 5,
            "tbs": "qdr:d"  # Dernières 24h
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            topics = []
            if "news_results" in results:
                for item in results["news_results"]:
                    topics.append({
                        'title': item.get('title', ''),
                        'trend': 'hot' if 'hour' in item.get('date', '') else 'warm'
                    })
            
            return topics
            
        except Exception as e:
            logger.error(f"Erreur trending topics: {e}")
            return []
    
    def _parse_serpapi_date(self, date_str: str) -> datetime:
        """Parse les dates de SerpAPI en datetime."""
        if not date_str:
            return None
            
        date_lower = date_str.lower()
        now = datetime.now()
        
        try:
            # Patterns relatifs
            if 'minute' in date_lower or 'min ago' in date_lower:
                # Extraire le nombre de minutes
                match = re.search(r'(\d+)\s*min', date_lower)
                if match:
                    minutes = int(match.group(1))
                    return now - timedelta(minutes=minutes)
                return now - timedelta(minutes=30)  # Par défaut
                
            elif 'hour' in date_lower or 'heure' in date_lower:
                match = re.search(r'(\d+)\s*h', date_lower)
                if match:
                    hours = int(match.group(1))
                    return now - timedelta(hours=hours)
                return now - timedelta(hours=1)
                
            elif 'today' in date_lower or "aujourd'hui" in date_lower:
                return now.replace(hour=12, minute=0, second=0)
                
            elif 'yesterday' in date_lower or 'hier' in date_lower:
                return now - timedelta(days=1)
                
            elif 'day' in date_lower or 'jour' in date_lower:
                match = re.search(r'(\d+)\s*day', date_lower)
                if match:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
                    
            elif 'week' in date_lower or 'semaine' in date_lower:
                match = re.search(r'(\d+)\s*week', date_lower)
                if match:
                    weeks = int(match.group(1))
                    return now - timedelta(weeks=weeks)
                    
            # Formats de date absolus
            # Format: Jan 15, 2025
            date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})'
            match = re.search(date_pattern, date_str, re.IGNORECASE)
            if match:
                month_abbr = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                month = month_abbr[match.group(1).lower()]
                day = int(match.group(2))
                year = int(match.group(3))
                return datetime(year, month, day)
                
        except Exception as e:
            logger.error(f"Erreur parsing date '{date_str}': {e}")
            
        return None