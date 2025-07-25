from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class SetModelView(APIView):
    """Endpoint pour changer le modèle LLM utilisé"""
    
    def post(self, request):
        """Change le modèle actif"""
        model = request.data.get('model', 'vllm')
        
        if model not in ['vllm', 'openrouter']:
            return Response(
                {'error': 'Modèle invalide. Choisir: vllm ou openrouter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Stocker le choix dans le cache
        cache.set('selected_llm_model', model, timeout=None)
        
        logger.info(f"🔄 Changement de modèle: {model}")
        
        # Vérifier que le cache a bien été mis à jour
        verify = cache.get('selected_llm_model')
        logger.info(f"✅ Vérification cache: {verify}")
        
        return Response({
            'success': True,
            'model': model,
            'message': f'Modèle changé vers {model}'
        })
    
    def get(self, request):
        """Récupère le modèle actuel"""
        model = cache.get('selected_llm_model', 'openrouter')
        
        return Response({
            'model': model
        })