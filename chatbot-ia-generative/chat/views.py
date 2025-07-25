from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
import httpx
import json
from django.conf import settings
from typing import List, Dict
from datetime import datetime, timedelta
import re

from .models import Conversation, Message, SearchCache
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ChatRequestSerializer
)
from .services.serpapi_service import SerpAPIService
from .services.multi_search import MultiSearchService  # Backup
from .services.openrouter_optimized import OpenRouterOptimizedService
from .services.intelligent_search import IntelligentSearchService
from .services.vllm_service import VLLMService
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Configuration simple des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class ChatAPIView(APIView):
    """Main chat endpoint for the chatbot."""
    
    throttle_classes = [AnonRateThrottle]
    
    def handle_chat(self, message_text: str, conversation_id: str = None):
        """Handle the chat request."""
        # Log simple pour nouvelle requête
        logger.info(f"💬 Nouvelle requête: {message_text[:50]}...")
        
        # Obtenir la date actuelle
        current_date = datetime.now()
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                raise ValidationError("Invalid conversation ID")
        else:
            conversation = Conversation.objects.create()
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_text
        )
        
        # Check if the message requires web search
        search_results = None
        sources = []
        search_query = None
        
        if self._requires_search(message_text):
            logger.info(f"🔍 Recherche web activée")
            time_constraint = self._extract_time_constraint(message_text)
            
            # Utiliser le service de recherche intelligent
            intelligent_search = IntelligentSearchService()
            search_result = intelligent_search.process_user_query(
                user_query=message_text,
                time_constraint=time_constraint,
                current_date=current_date
            )
            
            # Extraire la réponse et les sources
            ai_response = search_result.get('response', "Je n'ai pas pu traiter votre demande.")
            sources = search_result.get('sources', [])
            search_query = search_result.get('search_query')
            search_results = sources  # Pour la sauvegarde dans le message
            
        else:
            
            # Get conversation history
            messages = []
            for msg in conversation.messages.filter(role__in=['user', 'assistant']).order_by('created_at'):
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # Récupérer le modèle sélectionné
            selected_model = cache.get('selected_llm_model', 'vllm')
            logger.info(f"📌 Modèle sélectionné depuis le cache: {selected_model}")
            
            if selected_model == 'vllm':
                # Utiliser vLLM
                vllm_service = VLLMService()
                if not vllm_service.is_available():
                    logger.error(f"❌ vLLM n'est pas disponible sur {vllm_service.base_url}")
                    ai_response = "Erreur : Le service vLLM n'est pas disponible. Veuillez démarrer vLLM ou basculer sur OpenRouter."
                else:
                    try:
                        logger.info("🤖 MODE: vLLM Local (Phi-3)")
                        
                        # Construire le contexte de conversation
                        conversation_context = "\n".join([
                            f"{msg['role'].capitalize()}: {msg['content']}"
                            for msg in messages[:-1]
                        ])
                        
                        prompt = message_text
                        if conversation_context:
                            prompt = f"Conversation précédente:\n{conversation_context}\n\nQuestion: {message_text}"
                        
                        response = vllm_service.generate_response(prompt=prompt)
                        if response['success']:
                            ai_response = response['response']
                        else:
                            raise Exception(response['error'])
                    except Exception as e:
                        logger.error(f"❌ Erreur vLLM: {str(e)}")
                        ai_response = f"Erreur lors de la génération de la réponse : {str(e)}"
            else:
                # Utiliser OpenRouter
                try:
                    logger.info("☁️ MODE: OpenRouter Cloud (Qwen)")
                    openrouter_service = OpenRouterOptimizedService()
                    ai_response = openrouter_service.generate_response(
                        query=message_text,
                        search_results=None,
                        current_date=current_date,
                        conversation_history=messages[:-1]
                    )
                except Exception as e:
                    logger.error(f"❌ Erreur OpenRouter: {str(e)}")
                    ai_response = f"Erreur avec OpenRouter. Vérifiez votre clé API: {str(e)}"
        
        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response,
            search_results=search_results,
            sources=sources
        )
        
        return {
            'conversation_id': str(conversation.id),
            'message': MessageSerializer(assistant_message).data,
            'sources': sources,
            'search_query': search_query  # Inclure la requête optimisée dans la réponse
        }
    
    def post(self, request):
        """Handle POST request for chat."""
        
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        
        try:
            # Handle the chat request
            result = self.handle_chat(message, conversation_id)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return Response(
                {'error': 'An error occurred while processing your request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _requires_search(self, message: str) -> bool:
        """Determine if the message requires web search."""
        
        search_keywords = [
            'search', 'find', 'latest', 'recent', 'news', 'current',
            'today', 'update', 'développements', 'annoncés', 'cette semaine',
            'derniers', 'actuels', 'nouveautés', 'recherche'
        ]
        
        message_lower = message.lower()
        return any(kw in message_lower for kw in search_keywords)
    
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from the message."""
        
        # For now, use the entire message as search query
        # This can be enhanced with NLP techniques
        
        # Remove common question words
        remove_words = ['what', 'who', 'when', 'where', 'why', 'how', 'is', 'are', 
                       'qu\'est-ce', 'quels', 'quelles', 'comment', 'pourquoi']
        
        words = message.lower().split()
        filtered_words = [w for w in words if w not in remove_words]
        
        return ' '.join(filtered_words) if filtered_words else message
    
    # NOTE: perform_search is now handled by IntelligentSearchService
    # def perform_search(self, query: str) -> list:
    #     """Perform web search using Brave Search API."""
    #     This method is deprecated - use IntelligentSearchService instead
    
    # NOTE: extract_key_info is now handled by IntelligentSearchService
    # def extract_key_info(self, query: str, results: list) -> list:
    #     """Extract key information from search results."""
    #     This method is deprecated - use IntelligentSearchService instead
    
    # NOTE: generate_response is now handled by IntelligentSearchService for search queries
    # and OpenRouterOptimizedService for non-search queries
    # def generate_response(self, messages: list, search_results: list = None, current_date: datetime = None, time_constraint: str = None) -> str:
    #     """Generate response using OpenRouter API."""
    #     This method is deprecated - use IntelligentSearchService or OpenRouterOptimizedService instead
    
    
    def _extract_time_constraint(self, message: str) -> str:
        """Extract time constraint from the message."""
        message_lower = message.lower()
        
        # Patterns temporels
        time_patterns = {
            'cette semaine': 'this_week',
            'this week': 'this_week',
            'semaine dernière': 'last_week',
            'last week': 'last_week',
            'aujourd\'hui': 'today',
            'today': 'today',
            'hier': 'yesterday',
            'yesterday': 'yesterday',
            'ce mois': 'this_month',
            'this month': 'this_month',
            'mois dernier': 'last_month',
            'last month': 'last_month',
            'récent': 'recent',
            'recent': 'recent',
            'derniers': 'recent',
            'latest': 'recent'
        }
        
        for pattern, constraint in time_patterns.items():
            if pattern in message_lower:
                return constraint
        
        # Vérifier les patterns avec année
        year_pattern = r'(202[3-9]|20[3-9][0-9])'
        year_match = re.search(year_pattern, message)
        if year_match:
            return f'year_{year_match.group(1)}'
        
        return 'recent'  # Par défaut, chercher du contenu récent
    
    def _filter_by_date(self, results: List[Dict], time_constraint: str, current_date: datetime) -> List[Dict]:
        """Filter search results by date based on time constraint."""
        filtered = []
        
        # Définir la période de recherche
        if time_constraint == 'this_week':
            start_date = current_date - timedelta(days=current_date.weekday())
            end_date = current_date + timedelta(days=1)  # Inclure aujourd'hui
        elif time_constraint == 'last_week':
            start_date = current_date - timedelta(days=current_date.weekday() + 7)
            end_date = current_date - timedelta(days=current_date.weekday())
        elif time_constraint == 'today':
            start_date = current_date.replace(hour=0, minute=0, second=0)
            end_date = current_date + timedelta(days=1)
        elif time_constraint == 'yesterday':
            start_date = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            end_date = current_date.replace(hour=0, minute=0, second=0)
        elif time_constraint == 'this_month':
            start_date = current_date.replace(day=1)
            end_date = current_date + timedelta(days=1)
        elif time_constraint == 'recent':
            start_date = current_date - timedelta(days=7)  # Derniers 7 jours pour "recent"
            end_date = current_date + timedelta(days=1)
        else:
            # Pas de filtrage si contrainte non reconnue
            return results
        
        logger.info(f"📅 Filtrage temporel strict: {start_date.strftime('%d/%m/%Y %H:%M')} - {end_date.strftime('%d/%m/%Y %H:%M')}")
        logger.info(f"📅 Semaine actuelle: Semaine {current_date.isocalendar()[1]} de {current_date.year}")
        
        for result in results:
            # Utiliser date_parsed de SerpAPI si disponible
            result_date = None
            if result.get('date_parsed'):
                try:
                    # Parser la date ISO si c'est une string
                    if isinstance(result['date_parsed'], str):
                        result_date = datetime.fromisoformat(result['date_parsed'])
                    else:
                        result_date = result['date_parsed']
                except:
                    result_date = None
            
            # Sinon essayer d'extraire depuis le contenu
            if not result_date:
                result_date = self._extract_date_from_result(result)
            
            if result_date:
                # Vérification stricte de la période
                if start_date <= result_date <= end_date:
                    result['date'] = result_date.strftime('%d/%m/%Y %H:%M')
                    result['relevance_score'] = result.get('relevance_score', 0.8) * 1.2  # Boost pour dates correspondantes
                    filtered.append(result)
                    logger.info(f"✅ Résultat inclus: {result['title'][:50]}... - Date: {result['date']}")
                else:
                    logger.info(f"❌ Résultat exclu (hors période): {result['title'][:50]}... - Date: {result_date.strftime('%d/%m/%Y')}")
                    # Ne PAS inclure les résultats hors période
            else:
                # Si pas de date et contrainte temporelle stricte, exclure
                if time_constraint in ['this_week', 'today', 'yesterday']:
                    logger.info(f"❌ Résultat exclu (pas de date): {result['title'][:50]}...")
                else:
                    # Pour "recent", on peut être plus flexible
                    result['relevance_score'] = result.get('relevance_score', 0.5) * 0.7
                    result['date'] = 'Date non spécifiée'
                    filtered.append(result)
                    logger.info(f"⚠️ Résultat inclus avec score réduit: {result['title'][:50]}...")
        
        # Si aucun résultat, avertir mais ne pas retourner tous les résultats
        if not filtered:
            logger.warning(f"⚠️ Aucun résultat trouvé pour la période {time_constraint}")
            # Retourner seulement les 2 plus récents avec avertissement
            for r in results[:2]:
                r['relevance_score'] = 0.3
                r['warning'] = f"Hors période demandée ({time_constraint})"
            return results[:2]
        
        # Trier par date puis par pertinence
        def get_sort_date(item):
            if item.get('date_parsed'):
                try:
                    if isinstance(item['date_parsed'], str):
                        return datetime.fromisoformat(item['date_parsed'])
                    return item['date_parsed']
                except:
                    pass
            return datetime.min
            
        filtered.sort(key=lambda x: (
            get_sort_date(x),
            x.get('relevance_score', 0)
        ), reverse=True)
        
        return filtered
    
    def _extract_date_from_result(self, result: Dict) -> datetime:
        """Extract date from search result content or metadata."""
        # Chercher dans le contenu et le titre
        text = f"{result.get('title', '')} {result.get('content', '')} {result.get('snippet', '')}"
        
        # Patterns de dates
        date_patterns = [
            # Format: January 15, 2025
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
            # Format: 15 Jan 2025
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
            # Format: 2025-01-15
            r'(\d{4})-(\d{2})-(\d{2})',
            # Format: 15/01/2025 ou 01/15/2025
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Convertir le match en datetime selon le format
                    if 'January' in pattern:
                        # Format mois complet
                        month_names = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }
                        month = month_names[match.group(1).lower()]
                        day = int(match.group(2))
                        year = int(match.group(3))
                        return datetime(year, month, day)
                    elif 'Jan' in pattern:
                        # Format mois abrégé
                        month_abbr = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                        }
                        day = int(match.group(1))
                        month = month_abbr[match.group(2).lower()]
                        year = int(match.group(3))
                        return datetime(year, month, day)
                    elif '-' in pattern:
                        # Format ISO
                        year = int(match.group(1))
                        month = int(match.group(2))
                        day = int(match.group(3))
                        return datetime(year, month, day)
                except:
                    continue
        
        # Chercher des indications relatives
        if any(word in text.lower() for word in ['today', "aujourd'hui"]):
            return datetime.now()
        elif any(word in text.lower() for word in ['yesterday', 'hier']):
            return datetime.now() - timedelta(days=1)
        elif any(word in text.lower() for word in ['week', 'semaine']):
            # Approximation pour "cette semaine"
            return datetime.now() - timedelta(days=3)
        
        return None


class ConversationListView(APIView):
    """List all conversations."""
    
    def get(self, request):
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


class ConversationDetailView(APIView):
    """Get details of a specific conversation."""
    
    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
