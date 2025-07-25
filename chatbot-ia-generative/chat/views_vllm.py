from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from .services.vllm_service import VLLMService

logger = logging.getLogger(__name__)


class VLLMStatusView(APIView):
    """Check vLLM service status and model info."""
    
    def get(self, request):
        """Get vLLM status and model information."""
        vllm_service = VLLMService()
        
        is_available = vllm_service.is_available()
        models = []
        
        if is_available:
            models = vllm_service.list_models()
        
        return Response({
            'available': is_available,
            'base_url': vllm_service.base_url,
            'current_model': vllm_service.model,
            'available_models': models,
            'info': {
                'description': 'vLLM is a high-performance LLM serving engine',
                'features': [
                    'OpenAI-compatible API',
                    'High throughput serving',
                    'Continuous batching',
                    'PagedAttention for efficient memory usage'
                ]
            }
        })


class VLLMModelsView(APIView):
    """Get information about vLLM models."""
    
    def get(self, request):
        """List available models in vLLM."""
        vllm_service = VLLMService()
        
        if not vllm_service.is_available():
            return Response(
                {'error': 'vLLM service is not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        models = vllm_service.list_models()
        return Response({
            'models': models,
            'current_model': vllm_service.model,
            'note': 'vLLM typically serves one model at a time for optimal performance'
        })