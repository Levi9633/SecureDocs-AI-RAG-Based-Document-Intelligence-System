"""
RAG App — Views
Main AI chat endpoint that runs the full RAG pipeline:

POST /api/chat/
Body: { "chat_id": 1, "question": "Explain embeddings" }

Pipeline (per spec):
  1. Save user message
  2. Load last 15 messages (short-term memory)
  3. Load last 5 chat summaries (long-term memory)
  4. Generate query embedding
  5. FAISS retrieval → top 4 chunks
  6. Build full prompt
  7. Call Gemini → response
  8. Save assistant message
  9. Auto-generate title on first message
  10. Return answer + sources

Also handles: POST /api/chats/{id}/message/ (same pipeline, routed from chats urls)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chats.models import Chat
from chats.serializers import MessageSerializer
from chats import services as chat_services

from .retrieval import retrieve_chunks, format_retrieved_context, extract_sources
from .prompts import build_prompt
from .llm import generate_response, generate_title
from .memory import (
    get_recent_messages,
    format_recent_messages,
    get_recent_summaries,
    format_summaries,
)
from .vector_store import get_index_size


class RAGChatView(APIView):
    """
    POST /api/chat/
    The main RAG Q&A endpoint.
    """

    def post(self, request):
        chat_id = request.data.get('chat_id')
        question = request.data.get('question', '').strip()

        # ── Validation ──
        if not chat_id:
            return Response(
                {'error': 'chat_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not question:
            return Response(
                {'error': 'question cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify chat exists
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response(
                {'error': f'Chat {chat_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── Step 1: Save user message ──
        user_msg = chat_services.save_message(chat_id, 'user', question)

        # ── Step 2: Auto-generate title on first user message ──
        message_count = chat.messages.count()
        if message_count == 1:
            # This is the very first message — generate a title
            try:
                new_title = generate_title(question)
                if new_title and new_title != 'New Chat':
                    chat_services.rename_chat(chat_id, new_title)
            except Exception:
                pass  # Title generation is non-critical

        # ── Step 3: Load short-term memory (last 15 messages) ──
        recent_msgs = get_recent_messages(chat_id, n=15)
        recent_msgs_text = format_recent_messages(recent_msgs)

        # ── Step 4: Load long-term memory (last 5 chat summaries) ──
        summaries = get_recent_summaries(n=5)
        memory_text = format_summaries(summaries)

        # ── Step 5: FAISS Retrieval (top 4 chunks) ──
        retrieved = []
        sources = []
        retrieved_context = "No documents have been uploaded yet. Please upload documents to enable document-based Q&A."

        if get_index_size() > 0:
            retrieved = retrieve_chunks(question, k=4)
            if retrieved:
                retrieved_context = format_retrieved_context(retrieved)
                sources = extract_sources(retrieved)
            else:
                retrieved_context = "No relevant content found in uploaded documents for this question."

        # ── Step 6: Build full prompt ──
        prompt = build_prompt(
            memory=memory_text,
            recent_messages=recent_msgs_text,
            retrieved_chunks=retrieved_context,
            question=question,
        )

        # ── Step 7: Call Gemini ──
        answer = generate_response(prompt)

        # ── Step 8: Save assistant message ──
        assistant_msg = chat_services.save_message(chat_id, 'assistant', answer)

        # ── Step 9: Return response + sources ──
        return Response({
            'answer': answer,
            'sources': sources,
            'chat_id': chat_id,
            'message_id': assistant_msg.id,
        }, status=status.HTTP_200_OK)


class ChatMessageView(APIView):
    """
    POST /api/chats/{id}/message/
    Alternative endpoint to send a message — same RAG pipeline.
    Delegates to RAGChatView logic.
    """

    def post(self, request, chat_id):
        # Inject chat_id into request data and delegate
        data = request.data.copy()
        data['chat_id'] = chat_id
        request._full_data = data
        view = RAGChatView()
        view.request = request
        return view.post(request)
