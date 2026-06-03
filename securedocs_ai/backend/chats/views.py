"""
Chats App — Views (API Endpoints)

Endpoints per spec:
  POST   /api/chats/                   → Create new chat
  GET    /api/chats/                   → List all chats (sidebar)
  GET    /api/chats/{id}/              → Get single chat
  PATCH  /api/chats/{id}/              → Rename chat
  DELETE /api/chats/{id}/              → Delete chat
  GET    /api/chats/{id}/messages/     → Load all messages for chat window
  POST   /api/chats/{id}/summarize/    → Generate + store summary (New Chat flow)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, ChatDetailSerializer
from . import services
from rag.memory import summarize_and_store


from django.db.models import Count


class ChatListCreateView(APIView):
    """
    GET  /api/chats/ → list all chats for sidebar
    POST /api/chats/ → create new chat
    """

    def get(self, request):
        chats = Chat.objects.annotate(num_messages=Count('messages')).order_by('-updated_at')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request):
        title = request.data.get('title', 'New Chat')
        chat = services.create_chat(title=title)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatDetailView(APIView):
    """
    GET    /api/chats/{id}/ → single chat info
    PATCH  /api/chats/{id}/ → rename chat
    DELETE /api/chats/{id}/ → delete chat
    """

    def _get_chat(self, chat_id):
        try:
            return Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return None

    def get(self, request, chat_id):
        chat = self._get_chat(chat_id)
        if not chat:
            return Response({'error': f'Chat {chat_id} not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatDetailSerializer(chat)
        return Response(serializer.data)

    def patch(self, request, chat_id):
        title = request.data.get('title', '').strip()
        if not title:
            return Response({'error': 'Title cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            chat = services.rename_chat(chat_id, title)
            return Response(ChatSerializer(chat).data)
        except Chat.DoesNotExist:
            return Response({'error': f'Chat {chat_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, chat_id):
        try:
            services.delete_chat(chat_id)
            return Response({'message': 'Chat deleted.'}, status=status.HTTP_200_OK)
        except Chat.DoesNotExist:
            return Response({'error': f'Chat {chat_id} not found.'}, status=status.HTTP_404_NOT_FOUND)


class ChatMessagesView(APIView):
    """
    GET /api/chats/{id}/messages/ → load all messages for the chat window
    """

    def get(self, request, chat_id):
        if not Chat.objects.filter(id=chat_id).exists():
            return Response({'error': f'Chat {chat_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatSummarizeView(APIView):
    """
    POST /api/chats/{id}/summarize/
    New Chat workflow:
      1. Generate Gemini summary of current chat messages
      2. Store in ChatSummary table
      3. Return summary text
    Called BEFORE creating the new chat thread.
    """

    def post(self, request, chat_id):
        if not Chat.objects.filter(id=chat_id).exists():
            return Response({'error': f'Chat {chat_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        summary = summarize_and_store(chat_id)

        if summary is None:
            return Response({
                'message': 'No messages to summarize.',
                'summary': None
            })

        return Response({
            'message': 'Summary generated and stored.',
            'summary': summary,
            'chat_id': chat_id,
        })
