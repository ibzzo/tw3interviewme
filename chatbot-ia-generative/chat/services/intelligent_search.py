"""
Service de recherche intelligent avec génération de requête par LLM
"""
import httpx
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from django.conf import settings

from .serpapi_service import SerpAPIService
from .multi_search import MultiSearchService
from .vllm_service import VLLMService
from .openrouter_optimized import OpenRouterOptimizedService
from django.core.cache import cache

logger = logging.getLogger(__name__)


class IntelligentSearchService:
    """Service de recherche intelligent qui utilise le LLM pour optimiser les requêtes"""
    
    def __init__(self):
        # Services de recherche
        self.serpapi_service = SerpAPIService()
        self.multi_search = MultiSearchService()
        
        # Services LLM
        self.vllm_service = VLLMService()
        self.openrouter_service = OpenRouterOptimizedService()
        
        # Configuration OpenRouter pour les cas où on en a encore besoin
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Chatbot Intelligent Search"
        }
    
    def process_user_query(
        self,
        user_query: str,
        time_constraint: Optional[str] = None,
        current_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Traite la requête utilisateur en 2 étapes :
        1. Génère une requête de recherche optimisée
        2. Effectue la recherche et génère la réponse
        """
        
        try:
            # Étape 1: Générer la requête de recherche optimale
            search_query_data = self._generate_search_query(
                user_query, 
                time_constraint, 
                current_date
            )
            
            if not search_query_data.get('search_query'):
                logger.warning("❌ Pas de requête de recherche générée")
                return {
                    'response': "Je n'ai pas pu comprendre votre demande. Pouvez-vous reformuler?",
                    'sources': [],
                    'search_query': None
                }
            
            search_query = search_query_data['search_query']
            search_type = search_query_data.get('search_type', 'news')
            
            
            # Étape 2: Effectuer la recherche
            search_results = self._perform_smart_search(
                search_query, 
                search_type,
                time_constraint,
                current_date
            )
            
            # Étape 3: Générer la réponse finale avec le contexte
            final_response = self._generate_final_response(
                user_query,
                search_results,
                search_query,
                current_date,
                time_constraint
            )
            
            # Préparer les sources
            sources = []
            if search_results:
                sources = [
                    {
                        'title': r.get('title', ''),
                        'url': r.get('url', ''),
                        'date': r.get('date', ''),
                        'relevance_score': r.get('relevance_score', 0.5)
                    }
                    for r in search_results[:5]  # Top 5 sources
                ]
            
            return {
                'response': final_response,
                'sources': sources,
                'search_query': search_query,
                'search_type': search_type
            }
            
        except Exception as e:
            logger.error(f"Erreur recherche intelligente: {str(e)}", exc_info=True)
            return {
                'response': "Une erreur s'est produite lors du traitement de votre demande.",
                'sources': [],
                'error': str(e)
            }
    
    def _generate_search_query(
        self,
        user_query: str,
        time_constraint: Optional[str],
        current_date: Optional[datetime]
    ) -> Dict[str, str]:
        """
        Utilise le LLM pour générer une requête de recherche optimale
        """
        # Informations temporelles
        date_info = ""
        if current_date:
            date_info = f"\nDate actuelle: {current_date.strftime('%d/%m/%Y')} (Semaine {current_date.isocalendar()[1]})"
            if time_constraint:
                date_info += f"\nContrainte temporelle: {time_constraint}"
        
        # Prompt pour générer la requête
        system_prompt = f"""Tu es un expert en recherche web. Ta tâche est d'analyser la question de l'utilisateur et de générer LA MEILLEURE requête de recherche possible pour obtenir des informations pertinentes et actuelles.
{date_info}

INSTRUCTIONS:
1. Analyse la question pour identifier les concepts clés
2. Détermine s'il s'agit d'une recherche d'actualités, technique, ou générale
3. Génère une requête de recherche OPTIMISÉE qui maximisera la pertinence des résultats
4. Pour les actualités, ajoute des mots-clés temporels pertinents (2025, latest, announced, etc.)
5. Pour les sujets techniques, ajoute des termes spécifiques
6. Utilise des opérateurs de recherche si nécessaire (OR, "guillemets", etc.)

IMPORTANT: 
- La requête doit être EN ANGLAIS pour de meilleurs résultats
- Elle doit être concise mais précise
- Pour l'IA générative, privilégie les noms d'entreprises et de modèles spécifiques
- Pour les actualités récentes, ajoute TOUJOURS des termes temporels (today, this week, latest, announced)
- Inclus des noms de sociétés clés: OpenAI, Anthropic, Google, Meta, Microsoft

Réponds UNIQUEMENT avec un JSON structuré. Assure-toi que ta réponse est un JSON valide et rien d'autre:
{{
  "search_query": "la requête de recherche optimisée en anglais",
  "search_type": "news|technical|general",
  "keywords": ["mot1", "mot2", "mot3"],
  "reasoning": "explication courte de ta stratégie"
}}

IMPORTANT: Ta réponse doit être SEULEMENT le JSON, sans texte avant ou après."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question de l'utilisateur: {user_query}"}
        ]
        
        try:
            # Utiliser le modèle sélectionné dans le cache
            selected_model = cache.get('selected_llm_model', 'vllm')
            logger.info(f"🔎 Génération requête recherche avec: {selected_model}")
            
            if selected_model == 'vllm' and self.vllm_service.is_available():
                # Utiliser vLLM
                prompt = f"{system_prompt}\n\nUser: {messages[1]['content']}"
                response = self.vllm_service.generate_response(prompt=prompt)
                if response['success']:
                    response_text = response['response']
                    try:
                        # Parser le JSON
                        response_text = response_text.strip()
                        if '{' in response_text and '}' in response_text:
                            start = response_text.find('{')
                            end = response_text.rfind('}') + 1
                            json_str = response_text[start:end]
                            search_data = json.loads(json_str)
                            return search_data
                    except json.JSONDecodeError:
                        logger.warning("❌ JSON invalide de vLLM, fallback")
                        return {
                            'search_query': self._extract_query_from_text(user_query),
                            'search_type': 'general'
                        }
                else:
                    selected_model = 'openrouter'
            
            # Si OpenRouter ou si vLLM a échoué
            if selected_model == 'openrouter':
                response = httpx.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 200
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Parser le JSON
                    try:
                        # Nettoyer le contenu au cas où il y aurait du texte autour
                        content = content.strip()
                        # Essayer de trouver le JSON dans la réponse
                        if '{' in content and '}' in content:
                            start = content.find('{') 
                            end = content.rfind('}') + 1
                            json_str = content[start:end]
                            search_data = json.loads(json_str)
                            return search_data
                        else:
                            raise json.JSONDecodeError("No JSON found", content, 0)
                    except json.JSONDecodeError as e:
                        # Fallback: extraire la requête du texte
                        logger.warning(f"❌ Erreur parsing JSON: {e}")
                        logger.warning(f"❌ Contenu reçu: {content[:200]}...")
                        return {
                            'search_query': self._extract_query_from_text(user_query),
                            'search_type': 'general'
                        }
                elif response.status_code == 429:
                    logger.warning("⚠️ Limite OpenRouter atteinte (429) - Utilisation requête basique")
                    return {
                        'search_query': self._extract_query_from_text(user_query),
                        'search_type': 'general'
                    }
                else:
                    logger.error(f"Erreur API: {response.status_code}")
                    # Utiliser la requête originale en cas d'erreur
                    return {'search_query': user_query, 'search_type': 'general'}
                
        except Exception as e:
            logger.error(f"Erreur génération requête: {e}")
            # Fallback: utiliser la requête originale
            return {'search_query': user_query, 'search_type': 'general'}
    
    def _extract_query_from_text(self, text: str) -> str:
        """Extrait une requête de recherche optimisée du texte"""
        text_lower = text.lower()
        
        # Traductions et mots-clés
        translations = {
            'ia générative': 'generative AI',
            'intelligence artificielle': 'AI artificial intelligence',
            'développements': 'developments',
            'annoncés': 'announced',
            'cette semaine': 'this week',
            'derniers': 'latest',
            'récents': 'recent',
            'nouveaux': 'new',
            'exemples': 'examples'
        }
        
        # Remplacer les termes français par anglais
        query = text_lower
        for fr, en in translations.items():
            query = query.replace(fr, en)
        
        # Supprimer les mots interrogatifs
        remove_words = [
            'quels', 'sont', 'les', 'qu\'est-ce', 'que', 'comment',
            'pourquoi', 'où', 'quand', 'quel', 'quelle', 'donne-moi',
            'avec', 'leurs', 'sources', 'concrets'
        ]
        
        words = query.split()
        filtered = [w for w in words if w not in remove_words]
        
        # Ajouter l'année actuelle et des mots-clés pertinents
        filtered.extend(['2025', 'news', 'latest', 'announced', 'today'])
        
        # Ajouter des noms d'entreprises pour l'IA
        if 'generative' in query or 'ai' in query:
            filtered.extend(['OpenAI', 'Anthropic', 'Google', 'Meta', 'Microsoft'])
        
        # Construire la requête finale
        final_query = ' '.join(filtered)
        
        return final_query
    
    def _perform_smart_search(
        self,
        search_query: str,
        search_type: str,
        time_constraint: Optional[str],
        current_date: Optional[datetime]
    ) -> List[Dict]:
        """
        Effectue la recherche avec la requête optimisée
        """
        
        try:
            # Utiliser SerpAPI en priorité SANS cache pour les nouvelles recherches
            results = self.serpapi_service.search(
                query=search_query,
                search_type=search_type,
                use_cache=False  # Forcer une nouvelle recherche
            )
            
            # Si pas de résultats, essayer MultiSearch
            if not results:
                logger.warning("⚠️ Pas de résultats SerpAPI, essai MultiSearch")
                results = self.multi_search.search(search_query)
            
            # Filtrer par date si nécessaire
            # MAIS garder les résultats sans date si on n'a rien de mieux
            if time_constraint and results:
                filtered_results = self._filter_by_date(
                    results,
                    time_constraint,
                    current_date
                )
                # Si le filtrage supprime tout, garder les résultats originaux
                if not filtered_results and results:
                    logger.warning("⚠️ Aucun résultat avec date récente, utilisation des résultats sans date")
                    results = results[:5]  # Garder les 5 premiers
                else:
                    results = filtered_results
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche: {e}")
            return []
    
    def _filter_by_date(
        self,
        results: List[Dict],
        time_constraint: str,
        current_date: Optional[datetime]
    ) -> List[Dict]:
        """Filtre les résultats selon la contrainte temporelle"""
        if not current_date:
            current_date = datetime.now()
        
        # Définir la période
        if time_constraint == 'this_week':
            start_date = current_date - timedelta(days=current_date.weekday())
            end_date = current_date + timedelta(days=1)
        elif time_constraint == 'today':
            start_date = current_date.replace(hour=0, minute=0, second=0)
            end_date = current_date + timedelta(days=1)
        elif time_constraint == 'recent':
            start_date = current_date - timedelta(days=7)
            end_date = current_date + timedelta(days=1)
        else:
            return results
        
        filtered = []
        for result in results:
            # Utiliser date_parsed si disponible
            if result.get('date_parsed'):
                try:
                    if isinstance(result['date_parsed'], str):
                        result_date = datetime.fromisoformat(result['date_parsed'])
                    else:
                        result_date = result['date_parsed']
                    
                    if start_date <= result_date <= end_date:
                        filtered.append(result)
                except:
                    # Inclure avec score réduit si erreur
                    result['relevance_score'] = result.get('relevance_score', 0.5) * 0.7
                    filtered.append(result)
            else:
                # Pas de date, inclure selon le type
                if time_constraint not in ['this_week', 'today']:
                    result['relevance_score'] = result.get('relevance_score', 0.5) * 0.5
                    filtered.append(result)
        
        return filtered
    
    def _generate_final_response(
        self,
        user_query: str,
        search_results: List[Dict],
        search_query: str,
        current_date: Optional[datetime],
        time_constraint: Optional[str]
    ) -> str:
        """
        Génère la réponse finale en utilisant les résultats de recherche
        """
        if not search_results:
            return f"Je n'ai pas trouvé d'informations récentes pour votre recherche \"{search_query}\". Essayez de reformuler votre question ou de préciser ce que vous cherchez."
        
        # Formater le contexte
        context = self._format_search_context(search_results)
        
        # Informations temporelles
        date_info = ""
        if current_date:
            date_info = f"""
📅 DATE ACTUELLE: {current_date.strftime('%d/%m/%Y')}
📅 SEMAINE: {current_date.isocalendar()[1]} de {current_date.year}
⏰ PÉRIODE DEMANDÉE: {time_constraint or 'Non spécifiée'}
🔍 REQUÊTE DE RECHERCHE UTILISÉE: "{search_query}"
"""
        
        # Prompt pour la réponse finale
        system_prompt = f"""Tu es un assistant IA expert qui répond aux questions en utilisant EXCLUSIVEMENT les informations des résultats de recherche fournis.
{date_info}

🔴 RÈGLES ABSOLUES:
1. Tu DOIS baser ta réponse UNIQUEMENT sur le contexte ci-dessous
2. Tu DOIS citer chaque information avec [Source: Titre de l'article]
3. Si une information n'est pas dans le contexte, dis "Cette information n'est pas disponible dans les sources trouvées"
4. Structure ta réponse de manière claire et organisée
5. Termine TOUJOURS par une section "📚 Sources consultées:" avec les titres et URLs

📰 RÉSULTATS DE RECHERCHE (UTILISE UNIQUEMENT CES INFORMATIONS):
{context}

⚠️ NE PAS inventer ou utiliser des connaissances non présentes dans le contexte ci-dessus."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        try:
            # Utiliser le modèle sélectionné dans le cache
            selected_model = cache.get('selected_llm_model', 'vllm')
            logger.info(f"🔍 Génération réponse recherche avec: {selected_model}")
            
            if selected_model == 'vllm' and self.vllm_service.is_available():
                # Utiliser vLLM
                prompt = f"{system_prompt}\n\nQuestion: {user_query}"
                response = self.vllm_service.generate_response(prompt=prompt)
                if response['success']:
                    return response['response']
                else:
                    logger.error(f"Erreur vLLM: {response['error']}")
                    # Fallback vers OpenRouter
                    selected_model = 'openrouter'
            
            # Si OpenRouter ou si vLLM a échoué
            if selected_model == 'openrouter':
                response = httpx.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                elif response.status_code == 429:
                    logger.error("⚠️ Limite de taux OpenRouter atteinte (429)")
                    return "⚠️ Limite de requêtes OpenRouter atteinte. Veuillez patienter quelques minutes ou utiliser vLLM local."
                else:
                    logger.error(f"Erreur génération réponse: {response.status_code}")
                    return f"Erreur OpenRouter ({response.status_code}). Essayez vLLM local ou réessayez plus tard."
                
        except Exception as e:
            logger.error(f"Erreur réponse finale: {e}")
            return "Une erreur s'est produite lors de la génération de la réponse."
    
    def _format_search_context(self, search_results: List[Dict]) -> str:
        """Formate les résultats pour le contexte"""
        formatted = []
        
        for i, result in enumerate(search_results[:10], 1):  # Max 10 résultats
            title = result.get('title', 'Sans titre')
            url = result.get('url', '#')
            content = result.get('content', 'Contenu non disponible')
            date = result.get('date', 'Date non spécifiée')
            source = result.get('source', 'Source inconnue')
            
            formatted_result = f"""
=== RÉSULTAT {i} ===
📰 TITRE: {title}
🌐 SOURCE: {source}
📅 DATE DE PUBLICATION: {date}
🔗 URL: {url}
📝 CONTENU:
{content}
{'='*60}"""
            formatted.append(formatted_result)
        
        return "\n".join(formatted)