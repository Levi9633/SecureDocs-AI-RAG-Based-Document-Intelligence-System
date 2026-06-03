"""
Chats App Models
- Chat: conversation thread (id, title, created_at, updated_at)
- Message: individual message in a chat (id, chat_id FK, role, content, timestamp)
- ChatSummary: long-term memory summary of a closed chat (id, chat_id 1-to-1, summary, created_at)
"""

from django.db import models


class Chat(models.Model):
    """Represents a single conversation thread (like a ChatGPT conversation)."""
    title = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat #{self.id}: {self.title}"


class Message(models.Model):
    """A single message within a chat thread. Role: user | assistant | system."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] Chat #{self.chat_id} @ {self.timestamp}"


class ChatSummary(models.Model):
    """Long-term memory: OpenAI/Gemini-generated summary of a completed chat."""
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name='summary_obj')
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Summary for Chat #{self.chat_id}"
