"""
Chats App — URL Configuration
All chat-related API routes
"""

from django.urls import path
from . import views

urlpatterns = [
    # POST /api/chats/        → create new chat
    # GET  /api/chats/        → list all chats
    path('chats/', views.ChatListCreateView.as_view(), name='chat-list-create'),

    # GET    /api/chats/{id}/ → get single chat
    # PATCH  /api/chats/{id}/ → rename chat
    # DELETE /api/chats/{id}/ → delete chat
    path('chats/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat-detail'),

    # GET /api/chats/{id}/messages/ → load all messages
    path('chats/<int:chat_id>/messages/', views.ChatMessagesView.as_view(), name='chat-messages'),

    # POST /api/chats/{id}/summarize/ → generate + store summary (New Chat flow)
    path('chats/<int:chat_id>/summarize/', views.ChatSummarizeView.as_view(), name='chat-summarize'),
]
