from django.urls import path
from .views import ChatAPIView, ConversationListView, ConversationDetailView
from .views_vllm import VLLMStatusView, VLLMModelsView
from .views_model import SetModelView

app_name = 'chat'

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    # vLLM endpoints
    path('vllm/status/', VLLMStatusView.as_view(), name='vllm-status'),
    path('vllm/models/', VLLMModelsView.as_view(), name='vllm-models'),
    # Model selection
    path('set-model/', SetModelView.as_view(), name='set-model'),
]