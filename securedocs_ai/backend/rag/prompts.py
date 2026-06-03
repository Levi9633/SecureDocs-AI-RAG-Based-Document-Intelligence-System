"""
RAG — Prompt Builder
Constructs the full prompt per spec:

  System Prompt
  + Previous User Memory (last 5 summaries)
  + Recent Conversation (last 15 messages)
  + Retrieved Context (top 4 FAISS chunks)
  + Question
  → Answer:
"""

SYSTEM_PROMPT = """You are Levi AI — an intelligent document assistant powered by Gemini.

Your rules:
1. If the user asks for their name, who they are, or what was discussed in past chats, check the "PREVIOUS USER MEMORY" and "RECENT CONVERSATION" sections. If a name is mentioned (e.g., "introduced themselves as Shivu"), always address them by that name and respond conversationally and naturally.
2. If the user explicitly asks you to remember a fact (e.g., "remember this: [text]" or "remember that I prefer dark theme"), acknowledge it explicitly, confirm that you have stored it in your memory, and incorporate it in your future responses when relevant.
3. Be highly comprehensive and wise in your response formatting and detail based on the user's intent:
   - If the user asks to recall what was learned or discussed, scan the memory blocks thoroughly and list EVERY single topic, name, and concept covered. Do not omit any topics. Format this as a concise, readable bulleted list.
   - If the user asks to explain a concept, give a rich, detailed, and comprehensive explanation.
   - If the user asks a simple, direct question, keep the response short, clear, and direct.
4. For specific informational queries or questions about files, answer ONLY using the provided document context below. If the answer cannot be found in the uploaded documents or context, respond exactly:
   "Information not found in uploaded documents."
5. Never fabricate, guess, or hallucinate information.
6. Always cite your sources when referencing document context."""


def build_prompt(
    memory: str,
    recent_messages: str,
    retrieved_chunks: str,
    question: str
) -> str:
    """
    Build the complete prompt for Gemini.

    Prompt structure (per spec):
    System Prompt
    Previous User Memory: {memory}
    Recent Conversation: {recent_messages}
    Retrieved Context: {retrieved_chunks}
    Question: {question}
    Answer:
    """
    prompt = f"""{SYSTEM_PROMPT}

========================================
PREVIOUS USER MEMORY (Long-term context from past chats):
{memory if memory else "No previous conversation history."}

========================================
RECENT CONVERSATION (Short-term context — last 15 messages):
{recent_messages if recent_messages else "This is the start of the conversation."}

========================================
RETRIEVED DOCUMENT CONTEXT (Top relevant chunks from uploaded documents):
{retrieved_chunks if retrieved_chunks else "No documents have been uploaded yet."}

========================================
USER QUESTION:
{question}

ANSWER:"""

    return prompt


def build_summary_prompt(messages_text: str) -> str:
    """
    Build a prompt to summarize a completed conversation for long-term memory storage.
    """
    return f"""Generate a comprehensive summary of the following conversation.
Make sure to cover EVERY single topic, question, and document discussed. Do not omit any details, names, or key learning points.
Include the user's name if they introduced themselves.
CRITICAL: Prominently highlight any specific facts, preferences, or details that the user explicitly asked you to "remember" during the conversation, so they are permanently preserved in long-term memory.
Format the summary in clear, detailed bullet points.

CONVERSATION:
{messages_text}

SUMMARY:"""


def build_title_prompt(first_message: str) -> str:
    """
    Generate a short, descriptive chat title from the first user message.
    Example: "Explain neural networks" → "Neural Networks Basics"
    """
    return f"""Generate a very short title (3-5 words max) for a chat that starts with this message.
Return ONLY the title, nothing else.

Message: {first_message}
Title:"""
