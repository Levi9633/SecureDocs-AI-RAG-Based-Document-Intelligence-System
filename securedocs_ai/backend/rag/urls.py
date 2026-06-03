"""
RAG App — URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # POST /api/chat/ → main RAG Q&A endpoint
    path('chat/', views.RAGChatView.as_view(), name='rag-chat'),
]
