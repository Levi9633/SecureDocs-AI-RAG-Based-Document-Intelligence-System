"""
Chats App — Service Layer
Per spec service methods:
  - create_chat()
  - rename_chat()
  - delete_chat()
  - get_messages()
  - generate_and_store_summary() → called on New Chat
"""

from .models import Chat, Message, ChatSummary


def create_chat(title: str = 'New Chat') -> Chat:
    """Create a new conversation thread."""
    return Chat.objects.create(title=title)


def rename_chat(chat_id: int, title: str) -> Chat:
    """Rename an existing chat. Raises Chat.DoesNotExist if not found."""
    chat = Chat.objects.get(id=chat_id)
    chat.title = title
    chat.save(update_fields=['title', 'updated_at'])
    return chat


def delete_chat(chat_id: int) -> None:
    """
    Delete chat and all its messages and summary (CASCADE handles this).
    Raises Chat.DoesNotExist if not found.
    """
    chat = Chat.objects.get(id=chat_id)
    chat.delete()


def get_messages(chat_id: int) -> list:
    """Return all messages for a chat in chronological order."""
    return list(
        Message.objects
        .filter(chat_id=chat_id)
        .order_by('timestamp')
    )


def save_message(chat_id: int, role: str, content: str) -> Message:
    """Save a message to the database and touch the chat's updated_at."""
    msg = Message.objects.create(
        chat_id=chat_id,
        role=role,
        content=content,
    )
    # Touch updated_at on the parent chat
    Chat.objects.filter(id=chat_id).update(updated_at=msg.timestamp)
    return msg
