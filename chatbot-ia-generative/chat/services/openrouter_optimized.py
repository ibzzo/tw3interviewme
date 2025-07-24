"""
Service OpenRouter optimisé avec gestion stricte du contexte
"""
import httpx
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenRouterOptimizedService:
    """Service optimisé pour OpenRouter avec contexte forcé"""
    
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
    
    def generate_response(
        self, 
        query: str, 
        search_results: Optional[List[Dict]] = None,
        current_date: Optional[datetime] = None,
        time_constraint: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Génère une réponse en utilisant OpenRouter avec contexte de recherche forcé
        """
        logger.info(f"\n🤖 OPENROUTER - Génération de réponse")
        logger.info(f"📊 Modèle: {self.model}")
        
        try:
            messages = []
            
            # Si des résultats de recherche sont fournis, créer un prompt système strict
            if search_results:
                system_prompt = self._create_system_prompt_with_context(
                    search_results, 
                    current_date, 
                    time_constraint
                )
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
                # Ajouter l'historique de conversation si présent
                if conversation_history:
                    for msg in conversation_history[-5:]:  # Derniers 5 messages
                        if msg['role'] in ['user', 'assistant']:
                            messages.append(msg)
            else:
                # Prompt système simple sans recherche
                messages.append({
                    "role": "system",
                    "content": "Tu es un assistant IA utile et amical. Réponds de manière claire et concise en français."
                })
            
            # Ajouter la question de l'utilisateur
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Log pour debug
            logger.info(f"📝 Nombre de messages: {len(messages)}")
            if search_results:
                logger.info(f"🔍 Contexte de recherche: {len(search_results)} résultats")
            
            # Préparer la requête
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Plus bas pour plus de précision
                "max_tokens": 2000,
                "top_p": 0.9,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.1,
                "stream": False
            }
            
            # Faire la requête API
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30.0
            )
            
            logger.info(f"📡 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Nettoyer la réponse pour supprimer toute section de sources ajoutée
                ai_response = self._clean_response(ai_response)
                return ai_response
            else:
                error_detail = response.text
                logger.error(f"OpenRouter error: {response.status_code} - {error_detail}")
                
                # Détails spécifiques selon le code d'erreur
                if response.status_code == 401:
                    logger.error("❌ Erreur d'authentification - Vérifiez votre clé API OpenRouter")
                elif response.status_code == 429:
                    logger.error("❌ Limite de taux dépassée - Attendez avant de réessayer")
                elif response.status_code == 400:
                    logger.error(f"❌ Requête invalide - Détails: {error_detail}")
                
                return f"Désolé, une erreur s'est produite lors de la génération de la réponse. (Code: {response.status_code})"
                
        except httpx.TimeoutException:
            logger.error("OpenRouter timeout")
            return "Le service met trop de temps à répondre. Veuillez réessayer."
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            return f"Erreur lors de la génération: {str(e)}"
    
    def _create_system_prompt_with_context(
        self, 
        search_results: List[Dict], 
        current_date: Optional[datetime],
        time_constraint: Optional[str]
    ) -> str:
        """Crée un prompt système qui force l'utilisation du contexte"""
        
        # Informations temporelles
        date_info = ""
        if current_date:
            date_info = f"""
📅 DATE ACTUELLE: {current_date.strftime('%d/%m/%Y')}
📅 SEMAINE ACTUELLE: Semaine {current_date.isocalendar()[1]} de {current_date.year}
⏰ PÉRIODE DEMANDÉE: {time_constraint or 'Non spécifiée'}
"""
        
        # Formater le contexte de recherche
        context = self._format_search_results(search_results)
        
        # Prompt système strict
        system_prompt = f"""Tu es un assistant IA. Réponds en français en utilisant UNIQUEMENT les informations du contexte fourni.
{date_info}

RÈGLES STRICTES ET OBLIGATOIRES:

1. Base ta réponse UNIQUEMENT sur le contexte de recherche fourni
2. N'utilise PAS tes connaissances générales
3. Cite avec [1], [2], etc. selon le numéro de la source DANS LE TEXTE
4. NE PAS utiliser [Source: titre], utilise SEULEMENT [1], [2], etc.
5. INTERDICTION ABSOLUE d'ajouter une section "Sources consultées", "Sources:", ou toute liste d'URLs à la fin
6. INTERDICTION d'ajouter des liens ou URLs dans ta réponse
7. Termine ta réponse après le dernier paragraphe de contenu, SANS RIEN AJOUTER

CONTEXTE DE RECHERCHE:
{context}

IMPORTANT: Cite UNIQUEMENT avec [1], [2], etc. AUCUNE section "Sources" à la fin. AUCUN lien URL. Termine directement après ton dernier paragraphe."""
        
        return system_prompt
    
    def _format_search_results(self, search_results: List[Dict]) -> str:
        """Formate les résultats de recherche pour le contexte"""
        if not search_results:
            return "Aucun résultat de recherche disponible."
        
        formatted = []
        for i, result in enumerate(search_results, 1):
            # Extraire les informations importantes
            title = result.get('title', 'Sans titre')
            url = result.get('url', 'URL non disponible')
            content = result.get('content', 'Contenu non disponible')
            date = result.get('date', 'Date non spécifiée')
            source = result.get('source', 'Source inconnue')
            
            # Formater chaque résultat
            formatted_result = f"""
===== SOURCE [{i}] =====
TITRE: {title}
URL: {url}
DATE: {date}
CONTENU: {content}
{'=' * 50}"""
            formatted.append(formatted_result)
        
        return "\n".join(formatted)
    
    def _validate_source_usage(self, response: str, search_results: List[Dict]) -> bool:
        """Vérifie que la réponse utilise bien les sources"""
        response_lower = response.lower()
        
        # Patterns de citation
        citation_patterns = [
            "[source:",
            "source:",
            "selon",
            "d'après",
            "http"
        ]
        
        # Compter les citations
        citation_count = sum(1 for pattern in citation_patterns if pattern in response_lower)
        
        # Vérifier si au moins 30% des sources sont citées
        min_citations = max(1, len(search_results) // 3)
        
        # Vérifier aussi si des URLs sont mentionnées
        urls_mentioned = any(
            result.get('url', '').replace('https://', '').replace('http://', '') in response 
            for result in search_results
        )
        
        has_enough_citations = citation_count >= min_citations or urls_mentioned
        
        logger.info(f"📊 Validation citations: {citation_count} citations, URLs: {urls_mentioned}")
        
        return has_enough_citations
    
    def _add_source_reminder(self, response: str, search_results: List[Dict]) -> str:
        """Ne fait rien - on garde juste les citations inline"""
        return response
    
    def _clean_response(self, response: str) -> str:
        """Supprime toute section de sources à la fin de la réponse"""
        # Patterns à rechercher pour la section sources
        patterns = [
            r'\n\n📚\s*Sources consultées.*$',
            r'\n\nSources consultées.*$',
            r'\n\n📚\s*Sources\s*:.*$',
            r'\n\nSources\s*:.*$',
            r'\n\n##\s*Sources.*$',
            r'\n\n###\s*Sources.*$',
        ]
        
        import re
        cleaned = response
        
        # Supprimer tout ce qui suit ces patterns
        for pattern in patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE | re.DOTALL)
            if match:
                cleaned = cleaned[:match.start()]
                logger.info(f"✂️ Section sources supprimée")
                break
        
        # Supprimer aussi les citations [Source: ...] et les remplacer par des numéros si nécessaire
        cleaned = re.sub(r'\[Source:\s*[^\]]+\]', '', cleaned)
        
        return cleaned.strip()