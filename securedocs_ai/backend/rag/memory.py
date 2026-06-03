"""
RAG — Memory System
Implements both Short-term and Long-term memory per spec:

SHORT-TERM MEMORY:
  - Last 15 messages of the current chat
  - Included in every prompt for conversation continuity

LONG-TERM MEMORY:
  - Summaries of previous chats stored in ChatSummary table
  - Last 5 summaries loaded and injected into prompt
  - Generated when user clicks "New Chat"
"""

from chats.models import Message, ChatSummary, Chat
from .llm import generate_summary


def get_recent_messages(chat_id: int, n: int = 15) -> list[dict]:
    """
    Load the last N messages from a chat (short-term memory).
    Returns list of {role, content} dicts for prompt injection.
    """
    messages = (
        Message.objects
        .filter(chat_id=chat_id)
        .order_by('-timestamp')[:n]
        .values('role', 'content')
    )
    # Reverse to chronological order
    return list(reversed(list(messages)))


def format_recent_messages(messages: list[dict]) -> str:
    """
    Format recent messages as a readable conversation string for the prompt.
    """
    if not messages:
        return ""

    lines = []
    for msg in messages:
        role_label = msg['role'].capitalize()
        lines.append(f"{role_label}: {msg['content']}")

    return "\n".join(lines)


def get_recent_summaries(n: int = 5) -> list[str]:
    """
    Load the last N chat summaries (long-term memory).
    Returns list of summary strings from ChatSummary table.
    """
    return list(
        ChatSummary.objects
        .order_by('-created_at')[:n]
        .values_list('summary', flat=True)
    )


def format_summaries(summaries: list[str]) -> str:
    """
    Format chat summaries as a combined memory block for the prompt.
    """
    if not summaries:
        return ""

    parts = []
    for i, summary in enumerate(summaries, 1):
        parts.append(f"[Previous Chat {i}]\n{summary}")

    return "\n\n".join(parts)


def summarize_and_store(chat_id: int) -> str | None:
    """
    Generate a Gemini summary of all messages in a chat and store it.
    Called when user clicks "New Chat" to preserve long-term memory.

    Returns the summary string, or None if chat has no messages.
    """
    messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')

    if not messages.exists():
        return None

    # Format messages for summarization
    lines = []
    for msg in messages:
        lines.append(f"{msg.role.capitalize()}: {msg.content}")
    messages_text = "\n".join(lines)

    # Generate summary via Gemini
    summary_text = generate_summary(messages_text)

    # Store in ChatSummary table (upsert — update if exists)
    ChatSummary.objects.update_or_create(
        chat_id=chat_id,
        defaults={'summary': summary_text}
    )

    return summary_text
