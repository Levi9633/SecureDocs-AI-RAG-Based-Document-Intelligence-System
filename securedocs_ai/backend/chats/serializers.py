"""
Chats App Serializers
Handles JSON serialization for Chat, Message, ChatSummary
"""

from rest_framework import serializers
from .models import Chat, Message, ChatSummary


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'role', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ChatSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSummary
        fields = ['id', 'chat', 'summary', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    """Full chat object with message count for sidebar display."""
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return getattr(obj, 'num_messages', obj.messages.count())


class ChatDetailSerializer(serializers.ModelSerializer):
    """Chat with all its messages for chat window loading."""
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']
