from django.urls import path
from .views import ChatAPIView, ConversationListView, ConversationDetailView

app_name = 'chat'

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
]